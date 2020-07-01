import os

from ask_sdk.standard import StandardSkillBuilder

from command_handlers import (LaunchRequestHandler, StartLatestEpisodeHandler, StopEpisodeHandler, SearchEpisodeHandler,
                              ShuffleOnEpisodeHandler, ShuffleOffEpisodeHandler, StartOverEpisodeHandler,
                              RepeatEpisodeHandler,ResumeEpisodeHandler, HelpHandler, FallbackHandler, SessionEndedRequestHandler,
                              PreviousEpisodeHandler, NextEpisodeHandler, LoopOnEpisodeHandler, LoopOffEpisodeHandler)
from event_handlers import (PlaybackStoppedHandler, PlaybackFinishedHandler, PlaybackStartedHandler,
                            PlaybackFailedHandler, PlaybackNearlyFinishedHandler)
from interceptors import (SaveStateResponseInterceptor, LoadStateRequestInterceptor, RequestLogger, ResponseLogger,
                          CatchAllExceptionHandler)

streaming_table_name = os.getenv("STREAMING_TABLE_NAME")
skill_builder = StandardSkillBuilder(
    table_name=streaming_table_name,
    auto_create_table=False)

# Launch Request
skill_builder.add_request_handler(LaunchRequestHandler())

# Command Handlers
skill_builder.add_request_handler(StartLatestEpisodeHandler())
skill_builder.add_request_handler(SessionEndedRequestHandler())
skill_builder.add_request_handler(StopEpisodeHandler())
skill_builder.add_request_handler(ResumeEpisodeHandler())
skill_builder.add_request_handler(SearchEpisodeHandler())
skill_builder.add_request_handler(ShuffleOnEpisodeHandler())
skill_builder.add_request_handler(ShuffleOffEpisodeHandler())
skill_builder.add_request_handler(StartOverEpisodeHandler())
skill_builder.add_request_handler(RepeatEpisodeHandler())
skill_builder.add_request_handler(PreviousEpisodeHandler())
skill_builder.add_request_handler(NextEpisodeHandler())
skill_builder.add_request_handler(LoopOnEpisodeHandler())
skill_builder.add_request_handler(LoopOffEpisodeHandler())
skill_builder.add_request_handler(HelpHandler())
skill_builder.add_request_handler(FallbackHandler())

# Event Handlers
skill_builder.add_request_handler(PlaybackNearlyFinishedHandler())
skill_builder.add_request_handler(PlaybackFailedHandler())
skill_builder.add_request_handler(PlaybackStartedHandler())
skill_builder.add_request_handler(PlaybackStoppedHandler())
skill_builder.add_request_handler(PlaybackFinishedHandler())

# Request Interceptors
skill_builder.add_global_request_interceptor(RequestLogger())
skill_builder.add_global_request_interceptor(LoadStateRequestInterceptor())

# Response Interceptors
skill_builder.add_global_response_interceptor(ResponseLogger())
skill_builder.add_global_response_interceptor(SaveStateResponseInterceptor())

# Exception Handler
skill_builder.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = skill_builder.lambda_handler()
