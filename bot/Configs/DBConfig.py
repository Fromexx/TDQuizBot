DB_PATH = 'bot.db'

table_quiz  = 'CREATE TABLE IF NOT EXISTS quizzes ' \
'(id INTEGER PRIMARY KEY, ' \
'title TEXT NOT NULL);'

table_quest = 'CREATE TABLE IF NOT EXISTS questions ' \
'(id INTEGER PRIMARY KEY, ' \
'quiz_id  INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE, ' \
'text TEXT NOT NULL, ' \
'sort_order INTEGER NOT NULL);'


table_answers = 'CREATE TABLE IF NOT EXISTS user_answers ' \
'(id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
'user_id INTEGER NOT NULL, ' \
'question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE, ' \
'answer_text TEXT NOT NULL, ' \
'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'

TABLES = [table_quiz, table_quest, table_answers]
