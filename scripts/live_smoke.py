"""Opt-in live playlist validation; normal CI uses deterministic provider fixtures."""
import argparse
import json
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PyQt6.QtWidgets import QApplication
from mutagen import File
from pathvalidate import sanitize_filename
from tp_interface.app import MainWindow
from utils.Utils import MetadataPayload as MP
from process_checks import run_with_deadline


def validate(url, destination, timeout, max_tracks):
    if not shutil.which('ffmpeg'):
        raise RuntimeError('ffmpeg is required')
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise RuntimeError('Live validation requires an empty destination to protect existing files')
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    controller = window.ytSingleController
    window.ytDestinationInput.setText(str(destination.resolve()))
    window.ytUrlInput.setText(url)
    phase = 'retrieve'
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app.processEvents()
        if phase == 'retrieve' and window.ytDownloadButton.isEnabled():
            entries = [dict(p.getPayload()) for p in controller.metadataController.mdPayloads]
            if not 0 < len(entries) <= max_tracks:
                raise RuntimeError('Playlist size exceeds validation limit or contains no videos')
            filenames = [sanitize_filename(f'{entry[MP.TITLE]} - {entry[MP.ARTIST]}') + '.m4a'
                         for entry in entries]
            if len(set(name.casefold() for name in filenames)) != len(filenames):
                raise RuntimeError('Playlist has colliding filenames; OPT-002 must be fixed first')
            window.ytDownloadButton.click()
            phase = 'download'
        elif phase == 'download' and window.ytDownloadButton.isEnabled():
            state = controller.downloadState
            if state.n_download_failed or state.n_conversions_failed:
                raise RuntimeError(f'Batch errors: {state.n_download_failed} downloads, '
                                   f'{state.n_conversions_failed} conversions')
            if window.progressBar.value() != 100:
                raise RuntimeError('Batch did not reach 100%')
            for entry, filename in zip(entries, filenames):
                audio = File(destination / filename)
                if not audio or audio.info.length <= 0:
                    raise RuntimeError('Converted file is empty or invalid')
                if audio.tags.get('\xa9nam') != [entry[MP.TITLE]] or audio.tags.get('\xa9ART') != [entry[MP.ARTIST]]:
                    raise RuntimeError('Saved tags differ from reviewed metadata')
            if len(list(destination.glob('*.m4a'))) != len(entries):
                raise RuntimeError('Output file count differs from playlist count')
            if list(destination.glob('*.webm')):
                raise RuntimeError('Source deletion preference was not honored')
            controller.threadpool.waitForDone(1000)
            controller.metadataController.mdw.close()
            window.close()
            return {'tracks': len(entries), 'progress': 100, 'errors': 0,
                    'format': 'm4a', 'metadata_verified': True}
        elif phase == 'retrieve' and controller.threadpool.activeThreadCount() == 0:
            # Signals may still be queued; wait through another event cycle.
            app.processEvents()
            if not window.ytDownloadButton.isEnabled() and window.debugConsole.toPlainText():
                raise RuntimeError('Playlist retrieval failed; see YouTube availability/network')
        time.sleep(.02)
    # QThreadPool has no safe force-cancel API. The caller's process deadline
    # ensures a stalled provider cannot hang a manual/CI smoke check forever.
    raise TimeoutError('Live playlist validation exceeded its deadline')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--playlist', required=True)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--timeout', type=int, default=240)
    parser.add_argument('--max-tracks', type=int, default=5)
    parser.add_argument('--vpn-confirmed', action='store_true',
                        help='Explicitly acknowledge that a VPN is active for this necessary live test')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.vpn_confirmed:
        parser.error('Live testing is disabled unless a VPN is active and --vpn-confirmed is supplied')
    if not args.worker:
        raise SystemExit(run_with_deadline(
            [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:], '--worker'],
            timeout=args.timeout + 10,
        ))
    try:
        if args.destination:
            result = validate(args.playlist, args.destination, args.timeout, args.max_tracks)
        else:
            with tempfile.TemporaryDirectory(prefix='tek-plexor-live-') as folder:
                result = validate(args.playlist, Path(folder), args.timeout, args.max_tracks)
        print(json.dumps(result), flush=True)
    except Exception as error:
        print(f'Live validation failed: {error}', file=sys.stderr, flush=True)
        # Avoid blocking on destructor waits for an externally stalled QRunnable.
        os._exit(1)


if __name__ == '__main__':
    main()
