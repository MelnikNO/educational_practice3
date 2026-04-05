import sys
import re
import json
from collections import Counter
from pathlib import Path


# ЭТАП 1

class TextAnalyzer:
    """
    Класс для анализа текстовых файлов.
    Инкапсулирует все этапы обработки текста.
    """

    def __init__(self, filepath: str):
        """
        Инициализация анализатора.

        Аргументы:
            filepath: путь к текстовому файлу
        """
        self.filepath = filepath
        self.raw_text = ""  # Исходный текст
        self.cleaned_text = ""  # Очищенный текст
        self.words = []  # Список слов
        self.results = {}  # Результаты анализа

    # ЭТАП 2

    def read_file(self) -> bool:
        """
        Чтение файла с обработкой ошибок.

        Возвращает:
            True - файл прочитан успешно
            False - произошла ошибка
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                self.raw_text = file.read()

            if not self.raw_text.strip():
                print("⚠️ Внимание: файл пуст.")

            print(f"✓ Файл прочитан. Размер: {len(self.raw_text)} символов.")
            return True

        except FileNotFoundError:
            print(f"❌ Ошибка: Файл '{self.filepath}' не найден.")
            return False
        except UnicodeDecodeError:
            print(f"❌ Ошибка: Не удалось прочитать файл. Проверьте кодировку (UTF-8).")
            return False
        except Exception as e:
            print(f"❌ Ошибка при чтении: {e}")
            return False

    # ЭТАП 3

    def preprocess_text(self):
        """
        Предобработка текста:
        - приведение к нижнему регистру
        - удаление знаков препинания
        - нормализация пробелов
        """
        text_lower = self.raw_text.lower()

        # Удаляем знаки препинания, оставляем:
        # \w - буквы, цифры, подчёркивания
        # \s - пробелы
        # \- - дефис
        cleaned = re.sub(r'[^\w\s\-]', ' ', text_lower)

        # Убираем лишние пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        self.cleaned_text = cleaned
        print(f"✓ Текст предобработан.")

    # ЭТАП 4

    def tokenize(self):
        """
        Токенизация - разбиение текста на отдельные слова.
        """
        self.words = [word for word in self.cleaned_text.split() if word]
        print(f"✓ Токенизация завершена. Найдено слов: {len(self.words)}")

    # ЭТАП 5

    def analyze_word_statistics(self):
        """
        Анализ статистики слов:
        - общее количество слов
        - количество уникальных слов
        - топ-10 самых частотных слов
        - средняя длина слова
        """
        total_words = len(self.words)

        if total_words == 0:
            self.results['word_stats'] = {
                'total_words': 0,
                'unique_words': 0,
                'top10_words': [],
                'avg_word_length': 0
            }
            print("⚠️ Нет слов для анализа.")
            return

        # Уникальные слова через множество
        unique_words = len(set(self.words))

        # Частотный анализ с помощью Counter
        word_freq = Counter(self.words)
        top10 = word_freq.most_common(10)

        # Средняя длина слова
        avg_length = sum(len(word) for word in self.words) / total_words

        self.results['word_stats'] = {
            'total_words': total_words,
            'unique_words': unique_words,
            'top10_words': top10,
            'avg_word_length': round(avg_length, 2)
        }

        print(f"✓ Статистика слов вычислена:")
        print(f"Всего слов: {total_words}")
        print(f"Уникальных слов: {unique_words}")
        print(f"Средняя длина слова: {round(avg_length, 2)} симв.")

    # ЭТАП 6

    def count_sentences(self) -> int:
        """
        Определение количества предложений.
        Разделители: . ! ?
        """
        sentences = re.split(r'[.!?]+', self.raw_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)

    # ЭТАП 7

    def count_characters(self) -> dict:
        """
        Подсчёт символов:
        - с пробелами
        - без пробелов
        """
        total_chars = len(self.raw_text)

        chars_without_spaces = len(
            self.raw_text.replace(' ', '')
            .replace('\n', '')
            .replace('\t', '')
            .replace('\r', '')
        )

        return {
            'total_characters': total_chars,
            'characters_without_spaces': chars_without_spaces
        }

    # ЭТАП 8

    def detect_language_hint(self) -> str:
        """
        Упрощённое определение языка по частоте букв.
        """
        sample = self.raw_text[:1000].lower()

        russian = len(re.findall(r'[а-яё]', sample))
        english = len(re.findall(r'[a-z]', sample))

        if russian > english * 1.5:
            return "Русский"
        elif english > russian * 1.5:
            return "Английский"
        elif russian > 0 and english > 0:
            return "Смешанный"
        else:
            return "Не определён"

    # ЭТАП 9

    def print_report(self):
        """
        Вывод форматированного отчёта в консоль.
        """
        sentences = self.count_sentences()
        chars = self.count_characters()
        language = self.detect_language_hint()
        word_stats = self.results.get('word_stats', {})

        print("\n" + "=" * 60)
        print("📊 ОТЧЁТ АНАЛИЗА ТЕКСТА")
        print("=" * 60)

        print(f"\n📄 Файл: {self.filepath}")

        print(f"\n📝 СТАТИСТИКА ТЕКСТА:")
        print(f"• Язык (предположительно): {language}")
        print(f"• Количество предложений: {sentences}")
        print(f"• Всего символов: {chars['total_characters']}")
        print(f"• Символов без пробелов: {chars['characters_without_spaces']}")

        print(f"\n📖 СТАТИСТИКА СЛОВ:")
        print(f"• Всего слов: {word_stats.get('total_words', 0)}")
        print(f"• Уникальных слов: {word_stats.get('unique_words', 0)}")
        print(f"• Средняя длина слова: {word_stats.get('avg_word_length', 0)} симв.")

        print(f"\n🔥 ТОП-10 САМЫХ ЧАСТОТНЫХ СЛОВ:")
        top10 = word_stats.get('top10_words', [])
        if top10:
            for i, (word, count) in enumerate(top10, 1):
                display_word = word if len(word) <= 20 else word[:17] + "..."
                print(f"{i:2}. {display_word:<20} → {count:>4} раз(а)")
        else:
            print("Нет данных")

        print("\n" + "=" * 60)

    # ЭТАП 10

    def export_to_json(self):
        """
        Экспорт результатов в JSON-файл.
        """
        # Формируем полный словарь для экспорта
        export_data = {
            'file_info': {
                'file_path': self.filepath,
                'file_size_bytes': Path(self.filepath).stat().st_size
            },
            'text_statistics': {
                'sentences_count': self.count_sentences(),
                'characters': self.count_characters(),
                'language_hint': self.detect_language_hint()
            },
            'word_statistics': self.results.get('word_stats', {})
        }

        # Создаём имя выходного файла
        input_path = Path(self.filepath)
        output_path = input_path.parent / f"{input_path.stem}_analysis.json"

        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(export_data, json_file, ensure_ascii=False, indent=2)

        print(f"\n💾 Результаты сохранены в: {output_path}")

    # ЭТАП 11

    def run_full_analysis(self) -> bool:
        """
        Запуск полного анализа текста.

        Возвращает:
            True - анализ выполнен успешно
            False - произошла ошибка
        """
        print("\n" + "=" * 60)
        print("🔍 ЗАПУСК АНАЛИЗА ТЕКСТА")
        print("=" * 60 + "\n")

        if not self.read_file():
            return False

        self.preprocess_text()

        self.tokenize()

        self.analyze_word_statistics()

        return True


def main():
    """
    Главная функция программы.
    Обрабатывает аргументы командной строки.
    """
    if len(sys.argv) != 2:
        print("=" * 60)
        print("🔍 АНАЛИЗАТОР ТЕКСТА - Консольная программа")
        print("=" * 60)
        print("\nИспользование:")
        print(f"  python {sys.argv[0]} <путь_к_файлу>")
        print("\nПримеры:")
        print(f"  python {sys.argv[0]} text.txt")
        print(f"  python {sys.argv[0]} /home/user/document.txt")
        sys.exit(1)

    filepath = sys.argv[1]

    analyzer = TextAnalyzer(filepath)

    if analyzer.run_full_analysis():
        analyzer.print_report()
        analyzer.export_to_json()
        print("\n✅ Анализ завершён успешно!")
    else:
        print("\n❌ Анализ не выполнен из-за ошибок.")
        sys.exit(1)


if __name__ == "__main__":
    main()