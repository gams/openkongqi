# -*- coding: utf-8 -*-

from celery.utils.log import get_task_logger
import requests


HTTP_TIMEOUT = 10

logger = get_task_logger(__name__)


def fetch(req, timeout=None):
    """Wrap a :class:`Request <requests.Request>` in a session and send it.
    Any type of error (status code not 2xx or exceptions) will be handled here
    and the function then returns ``None``.

    :param req: :class:`Request <requests.Request>` instance
    :type req: requests.Request
    :param timeout: (optional) How long to wait for the server to send data
        before giving up
    :type timeout: float or tuple
    :rtype: requests.Response
    """
    if timeout is None:
        timeout = HTTP_TIMEOUT

    s = requests.Session()
    prepped = s.prepare_request(req)
    try:
        res = s.send(prepped, timeout=timeout)
    except requests.Timeout as e:
        logger.error("fetch error: timeout ({})".format(e.request.url))
        return
    except RequestException as e:
        logger.error("fetch error: {}".format(e.msg))
        return

    if res.status_code != requests.codes.ok:
        logger.error("fetch error: status {} ({})".format(
                res.status_code,
                req.url,
            )
        )
        logger.debug(res.text)
        return

    logger.debug("fetch success: {}".format(res.text))

    return res
