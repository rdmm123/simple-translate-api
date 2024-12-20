import ffmpeg
import subprocess

from ffmpeg.nodes import FilterableStream, OutputStream
from pathlib import Path
from typing import overload, Literal, cast, IO

from loguru import logger

class Compressor:
    DEFAULT_OUTPUT = Path("/tmp/output.mp4")
    def __init__(self) -> None:
        self._input_path: Path | None = None
        self._output_path: Path | None = None

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
            self.output_path = (
                self._input_path.parent / f'compressed_{self._input_path.name}'
                if self._input_path else self.DEFAULT_OUTPUT
            )
            self.output_path.unlink(missing_ok=True)
            filename = str(self.output_path)

        return ffmpeg.output(input, filename,
            vcodec='libx264',
            crf=23,
            preset='medium',
            acodec='aac',
            audio_bitrate='128k'
        )

    def _feed_input_pipe(self, input: IO[bytes], process: subprocess.Popen[bytes]) -> None:
        try:
            for chunk in iter(lambda: input.read(1024*1000), b""):
                process.stdin and process.stdin.write(chunk)
        finally:
            process.stdin and process.stdin.close()
            input.close()

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

        process: subprocess.Popen[bytes] = ffmpeg.run_async(output_stream, pipe_stdin=(not input_is_path), quiet=True)

        if not input_is_path:
            logger.debug("Feeding input to process stdin")
            self._feed_input_pipe(cast(IO[bytes], input), process)

        if output_mode == "path":
            logger.debug("Waiting for ffmpeg process to finalize")
            process.wait()
            assert self._output_path, "No output path for compressing"
            return self._output_path

        elif output_mode == "pipe":
            assert process.stdout is not None, "FFMPEG process stdout is None"
            return process.stdout


