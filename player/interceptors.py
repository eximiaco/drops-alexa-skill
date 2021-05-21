import logging
import json

from ask_sdk_core.dispatch_components import (
    AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)

from notifications import notify_error
from utils import DecimalEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Request and Response loggers


class RequestLogger(AbstractRequestInterceptor):
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Exception Handler


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        notify_error(exception)

        speech = "Desculpe. Tive um problema para obter os dados do podcast. Tente novamente mais tarde!"
        handler_input.response_builder.speak(speech)
        # .ask(speech)

        return handler_input.response_builder.response


# State Interceptors


class LoadStateRequestInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        state = handler_input.attributes_manager.persistent_attributes
        if len(state) == 0:
            state["playback"] = {
                "offset": 0,
                "repeat": False,
                "loop": False,
                "episode": None,
                "token": None,
                "firstTime": True
            }
        else:
            try:
                state["playback"] = {
                    "offset": int(state["playback"].get("offset")),
                    "repeat": bool(state["playback"].get("repeat")),
                    "loop": bool(state["playback"].get("loop")),
                    "episode": state["playback"].get("episode"),
                    "token": state["playback"].get("token"),
                    "firstTime": False
                }
            except:
                state["playback"] = {
                    "offset": 0,
                    "repeat": False,
                    "loop": False,
                    "episode": None,
                    "token": None,
                    "firstTime": False
                }


class SaveStateResponseInterceptor(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        try:
            handler_input.attributes_manager.save_persistent_attributes()
        except:
            print("Ocorreu um erro ao persistir os dados da sessão")
