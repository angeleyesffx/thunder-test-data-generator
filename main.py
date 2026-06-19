import logging
import sys

from api_sender import get_execution_list, generate_data_flow, thunder_exec
from commons.logger import setup_logging
from commons.requestBuilder import get_execution_stats
from environment import args, get_execute_flag

logger = logging.getLogger(__name__)


def main():
    setup_logging(verbose=args.verbose)
    try:
        flow, execution_list, report_list = get_execution_list(args)

        data_flow = None
        if flow:
            data_flow = generate_data_flow(execution_list)

        thunder_exec(execution_list, data_flow)

        for report in report_list:
            logger.warning(report)

        if get_execute_flag():
            stats = get_execution_stats()
            logger.info(
                "--- Execution summary: %d sent | %d success | %d failure ---",
                stats.total, stats.success, stats.failure,
            )

        has_failures = bool(report_list) or (get_execute_flag() and get_execution_stats().failure > 0)
        sys.exit(1 if has_failures else 0)

    except (KeyboardInterrupt, EOFError):
        sys.exit(0)


if __name__ == "__main__":
    main()
