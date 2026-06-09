import logging
import sys

from api_sender import get_execution_list, generate_data_flow, thunder_exec
from commons.logger import setup_logging
from environment import args

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

    except (KeyboardInterrupt, EOFError):
        sys.exit(0)


if __name__ == "__main__":
    main()
