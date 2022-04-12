import sys
import logging

def init(level: int):
	logger = logging.getLogger()
	logger.setLevel(level)

	file_formatter = logging.Formatter(
        "[{asctime}] [{levelname}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{"
    )

	if not sys.stdout.closed:
		stdout_handler = logging.StreamHandler(sys.stdout)
		stdout_handler.setFormatter(file_formatter)

		logger.addHandler(stdout_handler)


	logging.captureWarnings(True)