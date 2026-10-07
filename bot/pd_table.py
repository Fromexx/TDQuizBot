from Configs.DBConfig import DB_PATH
from DB.db import Table, QuizColumn, QuestionColumn, AnswerColumn
import pandas as pd
import sqlite3

db = sqlite3.connect(DB_PATH)
quizzes = pd.read_sql_query(f'SELECT * FROM {Table.QUIZZES}', db)
questions = pd.read_sql_query(f'SELECT * FROM {Table.QUESTIONS} ORDER BY {QuestionColumn.SORT_ORDER}', db)
answers = pd.read_sql_query(f'SELECT * FROM {Table.USER_ANSWERS}', db)

df = answers.merge(questions, left_on=AnswerColumn.QUESTION_ID, right_on=AnswerColumn.ID, suffixes=('_answer', '_question'))
df = df.merge(quizzes, left_on=QuestionColumn.QUIZ_ID, right_on=QuestionColumn.ID, suffixes=('', '_quiz'))

grouped = df.groupby([QuestionColumn.QUIZ_ID, QuestionColumn.ID, QuestionColumn.TEXT,QuestionColumn.SORT_ORDER])[AnswerColumn.ANSWER_TEXT].apply(list).reset_index()
grouped = grouped.sort_values([QuestionColumn.QUIZ_ID, QuestionColumn.SORT_ORDER])
