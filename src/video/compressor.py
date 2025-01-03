import ffmpeg
import subprocess
import threading

from ffmpeg.nodes import FilterableStream, OutputStream
from pathlib import Path
from typing import overload, Literal, cast, IO
from src.settings import get_settings

from loguru import logger


class Compressor:
    DEFAULT_OUTPUT = Path("/tmp/output.mp4")
    def __init__(self) -> None:
        self._input_path: Path | None = None
        self._output_path: Path | None = None
        self._settings = get_settings()

    def _get_input(self, input: Path | IO[bytes]) -> FilterableStream:
        if isinstance(input, Path):
            self._input_path = input
            return ffmpeg.input(str(input))

        return ffmpeg.input('pipe:')

    def _get_output(
        self, input: FilterableStream, mode: Literal["path", "pipe"]
    ) -> OutputStream:
        if mode == "pipe":
            filename = "pipe:"

        elif mode == "path":
            self._output_path = (
                self._input_path.parent / f'compressed_{self._input_path.stem}.mp4'
                if self._input_path else self.DEFAULT_OUTPUT
            )
            self._output_path.unlink(missing_ok=True)
            filename = str(self._output_path)

        return ffmpeg.output(
            input,
            filename=filename,
            vcodec="libx264",
            crf=23,
            preset="medium",
            acodec="aac",
            audio_bitrate="128k",
            f="mp4",
            # This is needed since mp4 needs to be seekable
            # So we need to use a fragmented mp4 if we want to stream the output
            movflags="+frag_keyframe+empty_moov" if mode == "pipe" else None,
        )

    def _feed_input_pipe(
        self, input: IO[bytes], process: subprocess.Popen[bytes]
    ) -> threading.Thread:
        def feed_input(input: IO[bytes], process: subprocess.Popen[bytes]) -> None:
            try:
                for chunk in iter(lambda: input.read(1024 * 1000), b""):
                    logger.debug("feeding bytes")
                    process.stdin and process.stdin.write(chunk)
            finally:
                process.stdin and process.stdin.close()
                input.close()

        thread = threading.Thread(target=feed_input, args=(input, process))
        thread.start()
        return thread

    @overload
    def compress_video(
        self, input: Path | IO[bytes], output_mode: Literal["path"]
    ) -> Path: ...
    @overload
    def compress_video(
        self, input: Path | IO[bytes], output_mode: Literal["pipe"]
    ) -> IO[bytes]: ...

    def compress_video(
        self, input: Path | IO[bytes], output_mode: Literal["path", "pipe"]
    ) -> Path | IO[bytes]:
        input_is_path = isinstance(input, Path)
        logger.info(f"Starting compression with {input_is_path=} and {output_mode=}")

        input_stream = self._get_input(input)
        output_stream = self._get_output(input_stream, output_mode)

        process: subprocess.Popen[bytes] = ffmpeg.run_async(
            output_stream,
            pipe_stdin=(not input_is_path),
            pipe_stdout=output_mode == 'pipe',
            quiet=self._settings.environment != "dev",
        )

        if not input_is_path:
            logger.debug("Feeding input to process stdin")
            thread = self._feed_input_pipe(cast(IO[bytes], input), process)

        if output_mode == "path":
            logger.debug("Waiting for ffmpeg process to finalize")
            process.wait()
            thread.join()
            assert self._output_path, "No output path for compressing"
            return self._output_path

        elif output_mode == "pipe":
            assert process.stdout is not None, "FFMPEG process stdout is None"
            return process.stdout


