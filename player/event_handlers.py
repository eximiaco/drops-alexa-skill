import ask_sdk_core.utils as ask_utils
import json

from player import Player
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model.interfaces.audioplayer import (PlayDirective, PlayBehavior, AudioItem, Stream, StopDirective)


# from  utils import DecimalEncoder

class PlaybackStartedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.handle_playback_started()

        return handler_input.response_builder.response


class PlaybackNearlyFinishedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.handle_playback_nearly_finished()

        return handler_input.response_builder.response


class PlaybackFailedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("AudioPlayer.PlaybackFailed")(handler_input)

    def handle(self, handler_input):
        speak_out = "Ocorreu um problema ao tocar o episódio solicitado. Tenta novamente mais tarde"
        handler_input.response_builder.speak(speak_out)

        return handler_input.response_builder.response


class PlaybackStoppedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.handle_playback_stopped()

        # json.dumps(handler_input.attributes_manager.persistent_attributes, indent=4,cls=DecimalEncoder)

        return handler_input.response_builder.response


class PlaybackFinishedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.handle_playback_finished()

        return handler_input.response_builder.response
