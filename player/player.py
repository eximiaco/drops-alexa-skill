from ask_sdk_model.interfaces.audioplayer import (PlayDirective, PlayBehavior, AudioItem, Stream, StopDirective)
from episodes_provider import EpisodesProvider


class Player(object):
    def __init__(self, handler_input):
        self.episodes_provider = EpisodesProvider()
        self.handler_input = handler_input
        self.state = PlayerState(handler_input.attributes_manager, self.episodes_provider)

    def reset(self):
        self.state.set_offset(0)

    # user interaction
    def play(self, episode):
        if episode is None:
            return False

        self.handler_input.response_builder.add_directive(
            PlayDirective(
                play_behavior=PlayBehavior.REPLACE_ALL,
                audio_item=AudioItem(
                    stream=Stream(
                        token=episode["pub"],
                        url=episode["address"],
                        offset_in_milliseconds=self.state.get_offset(),
                        expected_previous_token=None),
                    metadata=None))
        ).set_should_end_session(True)

        return True

    def play_latest(self):        
        episode = self.episodes_provider.get_latest()
        return self.play(episode)

    def is_playing_episode(self):
        current_episode = self.state.get_current_episode()
        if current_episode is None:
            return False
        return True

    def stop(self):
        self.handler_input.response_builder.add_directive(StopDirective())

    def resume(self):
        self.play(self.state.get_current_episode())

    def previous(self, jump_current_episode=True):
        current_episode = self.state.get_current_episode()
        if current_episode is None:
            return False

        self.reset()

        if jump_current_episode:
            self.disable_repeat()

            episode = self.episodes_provider.get_previous(current_episode)
            if episode is None and self.state.get_loop():
                episode = self.episodes_provider.get_latest()

            return self.play(episode)

        return self.play(current_episode)

    def next(self):
        current_episode = self.state.get_current_episode()
        if current_episode is None:
            return False

        self.reset()
        self.disable_repeat()

        episode = self.episodes_provider.get_next(current_episode)
        if episode is None and self.state.get_loop():
            episode = self.episodes_provider.get_first()

        return self.play(episode)

    # handlers
    def handle_playback_started(self):
        current_token = self.handler_input.request_envelope.request.token
        self.state.set_token(current_token)
        self.state.set_current_episode(current_token)

    def handle_playback_nearly_finished(self):
        current_episode = self.state.get_current_episode()
        if current_episode is None:
            return

        previous_episode = current_episode

        if not self.state.get_repeat():
            previous_episode = self.episodes_provider.get_previous(current_episode)

        if previous_episode is None and self.state.get_loop():
            previous_episode = self.episodes_provider.get_latest()

        if previous_episode is None:
            return

        self.handler_input.response_builder.add_directive(
            PlayDirective(
                play_behavior=PlayBehavior.ENQUEUE,
                audio_item=AudioItem(
                    stream=Stream(
                        token=previous_episode["pub"],
                        url=previous_episode["address"],
                        offset_in_milliseconds=0,
                        expected_previous_token=current_episode["pub"]),
                    metadata=None))
        ).set_should_end_session(True)

    def handle_playback_finished(self):
        self.reset()

    def handle_playback_stopped(self):
        millis = self.handler_input.request_envelope.request.offset_in_milliseconds
        print("handle_playback_stopped: {} millis".format(millis))
        self.state.set_offset(millis)

    # playback state
    def enable_repeat(self):
        self.state.set_repeat(True)

    def disable_repeat(self):
        self.state.set_repeat(False)

    def enable_loop(self):
        self.state.set_loop(True)

    def disable_loop(self):
        self.state.set_loop(False)


class PlayerState(object):

    def __init__(self, attributes_manager, episodes_provider):
        self.attributes_manager = attributes_manager
        self.episodes_provider = episodes_provider
        self.__current_episode = None

    def __get_state(self):
        return self.attributes_manager.persistent_attributes.get("playback")

    def get_offset(self):
        return self.__get_state().get("offset")

    def set_offset(self, value):
        self.__get_state()["offset"] = value

    def get_repeat(self):
        return self.__get_state().get("repeat")

    def set_repeat(self, value):
        self.__get_state()["repeat"] = value

    def get_loop(self):
        return self.__get_state().get("loop")

    def set_loop(self, value):
        self.__get_state()["loop"] = value

    def get_token(self):
        return self.__get_state().get("token")

    def set_token(self, value):
        self.__get_state()["token"] = value

    def get_current_episode(self):
        if self.__current_episode is not None:
            return self.__current_episode

        episode_pub = self.__get_state().get("episode")
        if episode_pub is None:
            return None

        return self.episodes_provider.get(episode_pub)

    def set_current_episode(self, value):
        self.__current_episode = None
        self.__get_state()["episode"] = value
