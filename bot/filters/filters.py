class isPol(Filter):
    async def __call__(self, message: Message) -> bool | dict:
        if not (message.text and message.text.startswith('/')):
            return False
        pol = message.text[1:]
        if pol in COMMANDS:
            return False
        titles_dict = await base.get_all(Table.QUIZZES, [QuizColumn.TITLE, QuizColumn.ID])
        id_titles = {titles['title']:titles['id'] for titles in titles_dict}
        if pol in list(id_titles.keys()):
            return {'PolName': (pol, id_titles[pol])}
        return False