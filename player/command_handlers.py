# coding=utf-8
import ask_sdk_core.utils as ask_utils
import os

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser

from player import Player
from episodes_provider import EpisodesProvider
from ask_sdk_core.dispatch_components import AbstractRequestHandler


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):

        player = Player(handler_input)
        player.reset()

        first_time = handler_input.attributes_manager.persistent_attributes.get("playback").get("firstTime")

        if first_time:
            speak_out = 'Olá, seja bem-vindo aos Drops da Exímia<emphasis level="strong">Cô</emphasis>. ' \
                        'Para começar você pode escolher o episódio mais recente dizendo: O mais recente, ' \
                        'ou ainda pesquisar sobre algum tema específico iniciando a frase com:  ' \
                        'O episódio sobre.<break time="500ms"/> ' \
                        'Para mais informações, basta me pedir Ajuda. ' \
                        '<break time="500ms"/>Qual episódio você gostaria de ouvir?'
        else:
            speak_out = 'Olá, seja bem-vindo de volta aos Drops da Exímia<emphasis level="strong">Cô</emphasis>. ' \
                        'Para qualquer dúvida, basta me pedir Ajuda. ' \
                        '<break time="500ms"/>Qual episódio você gostaria de ouvir?'

        handler_input.response_builder.speak(speak_out).ask(speak_out)

        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class StartLatestEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("PlayLatestEpisode")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)        
        player.play_latest()

        return handler_input.response_builder.response


class ResumeEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.resume()

        return handler_input.response_builder.response


class SearchEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SearchEpisode")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        provider = EpisodesProvider()

        search_term = ask_utils.get_slot_value(handler_input, "episode")
        session_attrs = handler_input.attributes_manager.session_attributes

        if len(session_attrs) == 0:
            self.search_episodes(handler_input, player, provider, search_term, session_attrs)
        else:
            self.filter_session_episodes(handler_input, player, provider, search_term, session_attrs)

        return handler_input.response_builder.response

    def filter_session_episodes(self, handler_input, player, provider, search_term, session_attrs):
        episodes_to_seek = session_attrs["episodes_to_seek"]
        if not os.path.exists("/tmp/indexepisodes"):
            os.mkdir("/tmp/indexepisodes")

        schema = Schema(title=(TEXT(stored=True)))
        ix = create_in("/tmp/indexepisodes", schema)

        writer = ix.writer()

        for ep in episodes_to_seek:
            writer.add_document(title=ep)

        writer.commit()
        title = None

        with ix.searcher() as searcher:
            query = QueryParser("title", ix.schema).parse(search_term)
            episode_titles = searcher.search(query)

            if len(episode_titles) > 0:
                title = episode_titles[0]["title"]

        if title is not None:
            episodes = provider.search(title)
            player.play(episodes[0])
        else:
            speak_out = "Nenhum dos episódios sugeridos fala sobre {}. " \
                        "Qual dos episódio sugeridos anteriormente você gostaria de ouvir?" \
                .format(search_term)

            handler_input.response_builder.speak(speak_out).ask(speak_out)

    def search_episodes(self, handler_input, player, provider, search_term, session_attrs):
        episodes = provider.search(search_term)
        episodes_count = 0 if episodes is None else len(episodes)

        print("episodes_count: {}", episodes_count)
        if episodes_count == 0:
            speak_out = "Não encontrei nenhum episódio sobre {}. Qual episódio você gostaria de ouvir?".format(
                search_term)
            handler_input.response_builder.speak(speak_out).ask(speak_out)
        elif episodes_count == 1:
            player.play(episodes[0])
        else:
            speak_out = "Encontrei {} episódios sobre {}. São eles:<break strength=\"strong\"/>".format(
                len(episodes), search_term)

            session_attrs["episodes_to_seek"] = []

            ix = 0
            for ep in episodes:
                title = ep["title"]
                session_attrs["episodes_to_seek"].append(title)

                ix = ix + 1
                speak_out = "{} {},<break strength=\"medium\"/>{}<break strength=\"strong\"/>; " \
                    .format(speak_out, ix, title)

            speak_out = "{}. Qual destes episódios você quer ouvir?".format(speak_out)
            handler_input.response_builder.speak(speak_out).ask(speak_out)


class StopEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.PauseIntent")(handler_input) \
               or ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) \
               or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.stop()

        return handler_input.response_builder.response


class ShuffleOnEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.ShuffleOnIntent")(handler_input)

    def handle(self, handler_input):
        speak_out = "Desculpe, mas não tenho suporte para ordenação aleatória de episódios"
        return handler_input.response_builder.speak(speak_out).response


class ShuffleOffEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.ShuffleOffIntent")(handler_input)

    def handle(self, handler_input):
        speak_out = "Desculpe, mas não tenho suporte para ordenação aleatória de episódios"
        return handler_input.response_builder.speak(speak_out).response


class StartOverEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)

        if not player.is_playing_episode():
            speak_out = 'Não posso reiniciar o episódio, pois nenhum episódio está sendo reproduzido no momento. ' \
                        'Para mais informações, basta me pedir ajuda. Qual episódio você gostaria de ouvir?'
            handler_input.response_builder.speak(speak_out).ask(speak_out)
        else:
            player.previous(False)
        return handler_input.response_builder.response


class HelpHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_out = '''Algumas coisas que você pode pedir para mim, nesta skill, são:<break time="1s"/>
        Avançar para o próximo episódio dizendo: próximo <break time="500ms"/>
        Voltar para o episódio anterior dizendo: anterior <break time="500ms"/>
        Parar a reprodução dizendo: parar <break time="500ms"/>
        Continuar a reprodução dizendo: continuar <break time="500ms"/>
        Escolher o episódio mais recente dizendo: O mais recente, ou o mais novo <break time="500ms"/>
        Escolher um episódio baseado em um tema. Exemplo: O episódio sobre trabalho remoto. 
        Se eu responder com uma lista, especialize ainda mais a sua consulta, usando o mesmo comando.
        O que você gostaria de fazer?'''

        handler_input.response_builder.speak(speak_out).ask(speak_out)
        return handler_input.response_builder.response


class RepeatEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # player = Player(handler_input)
        # player.enable_repeat()

        speak_out = "Desculpe, mas não tenho suporte para a função: Repetir"
        handler_input.response_builder.speak(speak_out)

        return handler_input.response_builder.response


class PreviousEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.PreviousIntent")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)

        if not player.is_playing_episode():
            speak_out = 'Não posso iniciar o episódio anterior, pois nenhum episódio está sendo reproduzido no momento. ' \
                        'Para mais informações, basta me pedir ajuda. Qual episódio você gostaria de ouvir?'
            handler_input.response_builder.speak(speak_out).ask(speak_out)
        else:
            if not player.previous():
                speak_out = 'Chegamos ao inicio da playlist, continue ouvindo este ou selecione outro episódio'
                handler_input.response_builder.speak(speak_out)

        return handler_input.response_builder.response


class NextEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.NextIntent")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)

        if not player.is_playing_episode():
            speak_out = 'Não posso iniciar o próximo episódio, pois nenhum episódio está sendo reproduzido no momento. ' \
                        'Para mais informações, basta me pedir ajuda. Qual episódio você gostaria de ouvir?'
            handler_input.response_builder.speak(speak_out).ask(speak_out)
        else:
            if not player.next():
                speak_out = 'Chegamos ao final da playlist, continue ouvindo este ou selecione outro episódio'
                handler_input.response_builder.speak(speak_out)

        return handler_input.response_builder.response


class LoopOnEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.LoopOnIntent")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.enable_loop()
        speak_out = "Loop da playlist ativado."
        handler_input.response_builder.speak(speak_out)

        return handler_input.response_builder.response


class LoopOffEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.LoopOffIntent")(handler_input)

    def handle(self, handler_input):
        player = Player(handler_input)
        player.disable_loop()
        speak_out = "Loop da playlist desativado."
        handler_input.response_builder.speak(speak_out)

        return handler_input.response_builder.response


class FallbackHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        speak_out = '''Desculpe, mas não entendi o seu comando. Você pode ouvir os comandos disponíveis 
        no Drops da Exímia<emphasis level="strong">Cô</emphasis>, pedindo Ajuda'''
        handler_input.response_builder.speak(speak_out).ask(speak_out)

        return handler_input.response_builder.response


class YesEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


class NoEpisodeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response
