import sys
import os
import math
import cmath
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QLabel,
    QComboBox,
    QTextEdit,
    QTabWidget,
    QFrame,
    QMessageBox,
    QDialog,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import (
    QFont,
    QKeySequence,
    QShortcut,
    QClipboard,
    QPalette,
    QColor,
    QIcon,
)


class CalculatorDisplay(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.setMinimumHeight(60)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #3daee9;
            }
        """)
        self.setText("0")


class CalculatorButton(QPushButton):
    def __init__(self, text, color_type="normal"):
        super().__init__(text)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.setMinimumSize(60, 50)

        colors = {
            "normal": {
                "bg": "#2d2d2d",
                "hover": "#3d3d3d",
                "pressed": "#4d4d4d",
                "text": "#ffffff",
            },
            "operation": {
                "bg": "#ff9500",
                "hover": "#ffad33",
                "pressed": "#cc7700",
                "text": "#ffffff",
            },
            "function": {
                "bg": "#505050",
                "hover": "#606060",
                "pressed": "#707070",
                "text": "#ffffff",
            },
            "clear": {
                "bg": "#a6a6a6",
                "hover": "#b6b6b6",
                "pressed": "#969696",
                "text": "#000000",
            },
            "equals": {
                "bg": "#ff9500",
                "hover": "#ffad33",
                "pressed": "#cc7700",
                "text": "#ffffff",
            },
        }

        style = colors[color_type]
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {style["bg"]};
                color: {style["text"]};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 2px;
            }}
            QPushButton:hover {{
                background-color: {style["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {style["pressed"]};
            }}
        """)


class EngineeringCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_input = "0"
        self.previous_input = ""
        self.operation = ""
        self.memory = 0
        self.angle_mode = "DEG"  # DEG, RAD, GRAD
        self.result_calculated = False
        self.history = []
        self.history_visible = False  # По умолчанию история скрыта
        self.second_mode = False  # Режим 2nd функций
        self.expression_mode = False  # Режим выражений

        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        self.setWindowTitle("Инженерный калькулятор")
        self.setWindowIcon(QIcon(os.path.join("img", "calc.ico")))
        self.setFixedSize(400, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QToolTip {
                background-color: #CCF0FE;
                color: blue;
                border: 2px dashed #FF0000;
                border-radius: 5px;
                padding: 3px 3px;
                font: 10pt "Segoe UI";
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Левая панель с калькулятором
        calc_widget = QWidget()
        calc_layout = QVBoxLayout()
        calc_widget.setLayout(calc_layout)

        # Дисплей
        self.display = CalculatorDisplay()
        calc_layout.addWidget(self.display)

        # Панель информации
        info_layout = QHBoxLayout()

        # Режим углов
        self.angle_label = QLabel(f"Углы: {self.angle_mode}")
        self.angle_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        info_layout.addWidget(self.angle_label)

        # Память
        self.memory_label = QLabel("M: 0")
        self.memory_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        info_layout.addWidget(self.memory_label)

        info_layout.addStretch()

        # Кнопка копирования
        copy_btn = QPushButton("")
        copy_btn.setIcon(QIcon(os.path.join("img", "copy.png")))
        copy_btn.setToolTip("Копировать результат")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4dbef9;
            }
        """)
        info_layout.addWidget(copy_btn)

        # Кнопка вставки
        paste_btn = QPushButton("")
        paste_btn.setIcon(QIcon(os.path.join("img", "paste.png")))
        paste_btn.setToolTip("Вставить из буфера обмена")
        paste_btn.clicked.connect(self.paste_from_clipboard)
        paste_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4dbef9;
            }
        """)
        info_layout.addWidget(paste_btn)

        # Кнопка показать/скрыть историю
        self.toggle_history_btn = QPushButton("")
        self.toggle_history_btn.setIcon(QIcon(os.path.join("img", "history.png")))
        self.toggle_history_btn.setToolTip("Показать/скрыть историю")
        self.toggle_history_btn.clicked.connect(self.toggle_history)
        self.toggle_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4dbef9;
            }
        """)
        info_layout.addWidget(self.toggle_history_btn)

        # Кнопка справки
        help_btn = QPushButton("")
        help_btn.setIcon(QIcon(os.path.join("img", "help.png")))
        help_btn.setToolTip("Справка")
        help_btn.clicked.connect(self.show_help)
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4dbef9;
            }
        """)
        info_layout.addWidget(help_btn)

        calc_layout.addLayout(info_layout)

        # Создание кнопок
        self.create_buttons(calc_layout)

        main_layout.addWidget(calc_widget, 2)

        # Правая панель с историей
        self.history_widget = QWidget()
        history_layout = QVBoxLayout()
        self.history_widget.setLayout(history_layout)

        history_label = QLabel("История вычислений")
        history_label.setStyleSheet(
            "color: #ffffff; font-weight: bold; font-size: 14px;"
        )
        history_layout.addWidget(history_label)

        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                font-family: Consolas;
                font-size: 12px;
            }
        """)
        history_layout.addWidget(self.history_display)

        clear_history_btn = QPushButton("Очистить историю")
        clear_history_btn.clicked.connect(self.clear_history)
        clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #dd5555;
            }
        """)
        history_layout.addWidget(clear_history_btn)

        main_layout.addWidget(self.history_widget, 1)

        # По умолчанию скрыть историю
        self.history_widget.setVisible(False)

    def create_buttons(self, layout):
        # Первый ряд - функции и операции
        row1_layout = QGridLayout()

        buttons_row1 = [
            ("2nd", "function"),
            ("π", "function"),
            ("e", "function"),
            ("C", "clear"),
            ("⌫", "clear"),
            ("MC", "function"),
            ("MR", "function"),
            ("M+", "function"),
            ("M-", "function"),
            ("MS", "function"),
        ]

        for i, (text, style) in enumerate(buttons_row1):
            btn = CalculatorButton(text, style)
            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            row1_layout.addWidget(btn, i // 5, i % 5)

            # Сохраняем ссылку на кнопку 2nd для изменения стиля
            if text == "2nd":
                self.second_btn = btn

        row1_layout.setSpacing(5)

        layout.addLayout(row1_layout)

        # Второй ряд - тригонометрические функции
        row2_layout = QGridLayout()

        buttons_row2 = [
            ("sin", "function"),
            ("cos", "function"),
            ("tan", "function"),
            ("DEG", "function"),
            ("(", "function"),
            ("asin", "function"),
            ("acos", "function"),
            ("atan", "function"),
            ("RAD", "function"),
            (")", "function"),
        ]

        for i, (text, style) in enumerate(buttons_row2):
            btn = CalculatorButton(text, style)
            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            row2_layout.addWidget(btn, i // 5, i % 5)

        row2_layout.setSpacing(5)

        layout.addLayout(row2_layout)

        # Третий ряд - логарифмы и степени
        row3_layout = QGridLayout()

        buttons_row3 = [
            ("ln", "function"),
            ("log", "function"),
            ("x²", "function"),
            ("x³", "function"),
            ("xʸ", "function"),
            ("eˣ", "function"),
            ("10ˣ", "function"),
            ("√", "function"),
            ("∛", "function"),
            ("ʸ√x", "function"),
        ]

        for i, (text, style) in enumerate(buttons_row3):
            btn = CalculatorButton(text, style)
            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))
            row3_layout.addWidget(btn, i // 5, i % 5)

        row3_layout.setSpacing(5)

        layout.addLayout(row3_layout)

        # Основные кнопки калькулятора
        main_layout = QGridLayout()

        buttons_main = [
            [
                ("7", "normal"),
                ("8", "normal"),
                ("9", "normal"),
                ("÷", "operation"),
                ("±", "function"),
            ],
            [
                ("4", "normal"),
                ("5", "normal"),
                ("6", "normal"),
                ("×", "operation"),
                ("1/x", "function"),
            ],
            [
                ("1", "normal"),
                ("2", "normal"),
                ("3", "normal"),
                ("-", "operation"),
                ("n!", "function"),
            ],
            [
                ("0", "normal"),
                (".", "normal"),
                ("=", "equals"),
                ("+", "operation"),
                ("%", "function"),
            ],
        ]

        for row, button_row in enumerate(buttons_main):
            for col, (text, style) in enumerate(button_row):
                btn = CalculatorButton(text, style)
                btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))
                main_layout.addWidget(btn, row, col)

        main_layout.setSpacing(5)

        layout.addLayout(main_layout)

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        shortcuts = {
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            "+": "+",
            "-": "-",
            "*": "×",
            "/": "÷",
            "=": "=",
            "Return": "=",
            "Enter": "=",
            ".": ".",
            ",": ".",
            "Backspace": "⌫",
            "Delete": "C",
            "Escape": "C",
            "Ctrl+C": "copy",
            "Ctrl+V": "paste",
            "F1": "help",
            "(": "(",
            ")": ")",
        }

        for key, action in shortcuts.items():
            if key == "Ctrl+C":
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(self.copy_to_clipboard)
            elif key == "Ctrl+V":
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(self.paste_from_clipboard)
            elif key == "F1":
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(self.show_help)
            else:
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(lambda a=action: self.on_button_click(a))

    def on_button_click(self, text):
        """Обработка нажатий кнопок"""
        try:
            if text.isdigit() or text == ".":
                self.input_number(text)
            elif text in ["+", "-", "×", "÷", "xʸ", "ʸ√x"]:
                self.input_operation(text)
            elif text == "=":
                self.calculate()
            elif text == "C":
                self.clear()
            elif text == "⌫":
                self.backspace()
            elif text == "±":
                self.toggle_sign()
            elif text in ["sin", "cos", "tan", "asin", "acos", "atan"]:
                self.trigonometric_function(text)
            elif text in ["ln", "log", "eˣ", "10ˣ"]:
                self.logarithmic_function(text)
            elif text in ["√", "∛", "x²", "x³"]:
                self.power_function(text)
            elif text in ["1/x", "n!"]:
                self.special_function(text)
            elif text == "%":
                self.percentage_operation()
            elif text in ["π", "e"]:
                self.input_constant(text)
            elif text in ["DEG", "RAD", "GRAD"]:
                self.change_angle_mode(text)
            elif text in ["MC", "MR", "M+", "M-", "MS"]:
                self.memory_operation(text)
            elif text in ["(", ")"]:
                self.input_parentheses(text)
            elif text == "2nd":
                self.toggle_second_mode()
        except Exception as e:
            self.display.setText("Ошибка")
            self.add_to_history(f"Ошибка: {str(e)}")

    def input_number(self, digit):
        """Ввод числа"""
        if self.current_input == "0" or self.result_calculated:
            self.current_input = digit if digit != "." else "0."
            self.result_calculated = False
        else:
            # Проверяем, можно ли вводить точку
            if digit == ".":
                # Ищем последнее число в выражении
                last_number_start = (
                    max(
                        self.current_input.rfind("+"),
                        self.current_input.rfind("-"),
                        self.current_input.rfind("×"),
                        self.current_input.rfind("÷"),
                        self.current_input.rfind("("),
                    )
                    + 1
                )

                last_number = self.current_input[last_number_start:]
                if "." in last_number:
                    return  # Уже есть точка в текущем числе

            self.current_input += digit
        self.update_display()

    def input_operation(self, op):
        """Ввод операции"""
        # Отладочная информация
        # print(f"DEBUG: input_operation('{op}')")
        # print(f"DEBUG: current_input = '{self.current_input}'")
        # print(f"DEBUG: expression_mode = {self.expression_mode}")
        # print(f"DEBUG: result_calculated = {self.result_calculated}")

        # Если есть скобки - всегда режим выражений
        if "(" in self.current_input or ")" in self.current_input:
            self.expression_mode = True
            if self.current_input and self.current_input[-1] not in "+-×÷":
                self.current_input += op
            self.update_display()
            return

        # Если уже в режиме выражений - продолжаем
        if self.expression_mode:
            if self.current_input and self.current_input[-1] not in "+-×÷":
                self.current_input += op
            self.update_display()
            return

        # Проверяем, есть ли уже операция в строке
        if any(char in self.current_input for char in "+-×÷"):
            # Переключаемся в режим выражений
            self.expression_mode = True
            if self.current_input and self.current_input[-1] not in "+-×÷":
                self.current_input += op
            self.update_display()
            return

        # Обычная логика для простых операций
        if self.operation and not self.result_calculated:
            self.calculate()

        # Если мы в режиме result_calculated, то добавляем операцию к текущему результату
        if self.result_calculated:
            # Переключаемся в режим выражений для составных операций
            self.expression_mode = True
            if self.current_input and self.current_input[-1] not in "+-×÷":
                self.current_input += op
            self.result_calculated = False
            self.update_display()
            return

        # Стандартная логика - добавляем операцию к строке
        self.expression_mode = True
        self.current_input += op
        self.result_calculated = False
        self.update_display()

    def input_parentheses(self, paren):
        """Ввод скобок"""
        # Скобки всегда переключают в режим выражений
        self.expression_mode = True

        # Отладочная информация
        # print(f"DEBUG: input_parentheses('{paren}')")
        # print(f"DEBUG: current_input = '{self.current_input}'")
        # print(f"DEBUG: result_calculated = {self.result_calculated}")

        if paren == "(":
            if self.current_input == "0":
                self.current_input = paren
                self.result_calculated = False
            elif self.result_calculated:
                # Если результат уже вычислен, добавляем умножение
                self.current_input += "×" + paren
                self.result_calculated = False
            else:
                last_char = self.current_input[-1]
                if last_char in "+-×÷(":
                    self.current_input += paren
                elif last_char.isdigit() or last_char == ")" or last_char == ".":
                    self.current_input += "×" + paren
                else:
                    self.current_input += paren
        else:  # paren == ")"
            if self.current_input == "0":
                return  # Нельзя начинать с закрывающей скобки

            open_count = self.current_input.count("(")
            close_count = self.current_input.count(")")
            last_char = self.current_input[-1]

            if open_count > close_count and (
                last_char.isdigit() or last_char == ")" or last_char == "."
            ):
                self.current_input += paren

        # print(f"DEBUG: final current_input = '{self.current_input}'")
        self.update_display()

    def calculate(self):
        """Вычисление"""
        try:
            # Если в режиме выражений - используем парсер
            if self.expression_mode:
                expression = self.current_input

                # Проверяем незакрытые скобки
                if expression.count("(") != expression.count(")"):
                    self.display.setText("Ошибка: незакрытые скобки")
                    self.add_to_history("Ошибка: незакрытые скобки")
                    return

                # Вычисляем выражение
                result = self.evaluate_expression(expression)

                # Добавляем в историю
                self.add_to_history(f"{self.current_input} = {result}")

                # Сбрасываем режим выражений
                self.expression_mode = False
                self.current_input = str(result)
                self.operation = ""
                self.previous_input = ""
                self.result_calculated = True
                self.update_display()
                return

            # Обычное вычисление
            if not self.operation or not self.previous_input:
                return

            prev = float(self.previous_input)
            curr = float(self.current_input)

            operations = {
                "+": prev + curr,
                "-": prev - curr,
                "×": prev * curr,
                "÷": prev / curr if curr != 0 else float("inf"),
                "xʸ": prev**curr,
                "ʸ√x": curr ** (1 / prev) if prev != 0 else float("inf"),
            }

            result = operations.get(self.operation, 0)

            # Добавляем в историю
            self.add_to_history(
                f"{self.previous_input} {self.operation} {self.current_input} = {result}"
            )

            self.current_input = str(result)
            self.operation = ""
            self.previous_input = ""
            self.result_calculated = True
            self.update_display()

        except Exception as e:
            self.display.setText("Ошибка")
            self.add_to_history(f"Ошибка вычисления: {str(e)}")

    def evaluate_expression(self, expression):
        """Безопасное вычисление математического выражения"""
        # Заменяем символы на стандартные операторы
        expression = expression.replace("×", "*").replace("÷", "/")

        # Обрабатываем специальные операции степени
        expression = expression.replace("xʸ", "**")

        # Обрабатываем операцию корня ʸ√x
        # Паттерн: число + ʸ√x + число → второе число в степени (1/первое число)
        import re

        # Ищем паттерн: число + ʸ√x + число
        pattern = r"(\d+(?:\.\d+)?)ʸ√x(\d+(?:\.\d+)?)"

        def replace_root(match):
            root_degree = match.group(1)  # степень корня
            number = match.group(2)  # число под корнем
            return f"({number})**(1/({root_degree}))"

        expression = re.sub(pattern, replace_root, expression)

        # Токенизируем выражение
        tokens = self.tokenize(expression)

        # Преобразуем в постфиксную нотацию
        postfix = self.infix_to_postfix(tokens)

        # Вычисляем результат
        return self.evaluate_postfix(postfix)

    def tokenize(self, expression):
        """Разбиение выражения на токены"""
        tokens = []
        i = 0

        while i < len(expression):
            char = expression[i]

            if char.isdigit() or char == ".":
                # Собираем число
                number = ""
                while i < len(expression) and (
                    expression[i].isdigit() or expression[i] == "."
                ):
                    number += expression[i]
                    i += 1
                tokens.append(float(number))
                continue
            elif char == "*" and i + 1 < len(expression) and expression[i + 1] == "*":
                # Обрабатываем оператор степени **
                tokens.append("**")
                i += 2
                continue
            elif char in "+-*/()":
                tokens.append(char)
            elif char == " ":
                pass  # Пропускаем пробелы
            else:
                raise ValueError(f"Неизвестный символ: {char}")

            i += 1

        return tokens

    def infix_to_postfix(self, tokens):
        """Преобразование инфиксной нотации в постфиксную"""
        precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "**": 3}
        stack = []
        output = []

        for token in tokens:
            if isinstance(token, (int, float)):
                output.append(token)
            elif token == "(":
                stack.append(token)
            elif token == ")":
                while stack and stack[-1] != "(":
                    output.append(stack.pop())
                if stack:
                    stack.pop()  # Удаляем '('
            elif token in precedence:
                # Для операции ** (степень) - правоассоциативная
                if token == "**":
                    while (
                        stack
                        and stack[-1] != "("
                        and stack[-1] in precedence
                        and precedence[stack[-1]] > precedence[token]
                    ):
                        output.append(stack.pop())
                else:
                    while (
                        stack
                        and stack[-1] != "("
                        and stack[-1] in precedence
                        and precedence[stack[-1]] >= precedence[token]
                    ):
                        output.append(stack.pop())
                stack.append(token)

        while stack:
            output.append(stack.pop())

        return output

    def evaluate_postfix(self, postfix):
        """Вычисление постфиксного выражения"""
        stack = []

        for token in postfix:
            if isinstance(token, (int, float)):
                stack.append(token)
            else:
                if len(stack) < 2:
                    raise ValueError("Некорректное выражение")

                b = stack.pop()
                a = stack.pop()

                if token == "+":
                    result = a + b
                elif token == "-":
                    result = a - b
                elif token == "*":
                    result = a * b
                elif token == "/":
                    if b == 0:
                        raise ValueError("Деление на ноль")
                    result = a / b
                elif token == "**":
                    result = a**b
                else:
                    raise ValueError(f"Неизвестная операция: {token}")

                stack.append(result)

        if len(stack) != 1:
            raise ValueError("Некорректное выражение")

        return stack[0]

    def trigonometric_function(self, func):
        try:
            value = float(self.current_input)

            # Проверяем режим 2nd для автоматического переключения функций
            if self.second_mode:
                second_functions = {"sin": "asin", "cos": "acos", "tan": "atan"}
                if func in second_functions:
                    func = second_functions[func]
                    self.reset_second_mode()

            # Конвертация углов
            if func in ["sin", "cos", "tan"]:
                if self.angle_mode == "DEG":
                    value = math.radians(value)
                elif self.angle_mode == "GRAD":
                    value = value * math.pi / 200

            functions = {
                "sin": math.sin(value),
                "cos": math.cos(value),
                "tan": math.tan(value),
                "asin": math.asin(value) if -1 <= value <= 1 else float("nan"),
                "acos": math.acos(value) if -1 <= value <= 1 else float("nan"),
                "atan": math.atan(value),
            }

            result = functions[func]

            # Конвертация результата для обратных функций
            if func in ["asin", "acos", "atan"]:
                if self.angle_mode == "DEG":
                    result = math.degrees(result)
                elif self.angle_mode == "GRAD":
                    result = result * 200 / math.pi

            self.add_to_history(f"{func}({self.current_input}) = {result}")
            self.current_input = str(result)
            self.result_calculated = True
            self.expression_mode = False  # Сбрасываем режим выражений
            self.update_display()

        except Exception as e:
            self.display.setText("Ошибка")
            self.add_to_history(f"Ошибка в {func}: {str(e)}")

    def logarithmic_function(self, func):
        try:
            value = float(self.current_input)

            # Проверяем режим 2nd для автоматического переключения функций
            if self.second_mode:
                second_functions = {"ln": "eˣ", "log": "10ˣ"}
                if func in second_functions:
                    func = second_functions[func]
                    self.reset_second_mode()

            functions = {
                "ln": math.log(value) if value > 0 else float("nan"),
                "log": math.log10(value) if value > 0 else float("nan"),
                "eˣ": math.exp(value),
                "10ˣ": 10**value,
            }

            result = functions[func]
            self.add_to_history(f"{func}({self.current_input}) = {result}")
            self.current_input = str(result)
            self.result_calculated = True
            self.expression_mode = False  # Сбрасываем режим выражений
            self.update_display()

        except Exception as e:
            self.display.setText("Ошибка")
            self.add_to_history(f"Ошибка в {func}: {str(e)}")

    def power_function(self, func):
        try:
            value = float(self.current_input)

            # Проверяем режим 2nd для автоматического переключения функций
            if self.second_mode:
                second_functions = {"x²": "√", "x³": "∛"}
                if func in second_functions:
                    func = second_functions[func]
                    self.reset_second_mode()

            functions = {
                "√": math.sqrt(value) if value >= 0 else float("nan"),
                "∛": value ** (1 / 3),
                "x²": value**2,
                "x³": value**3,
            }

            result = functions[func]
            self.add_to_history(f"{func}({self.current_input}) = {result}")
            self.current_input = str(result)
            self.result_calculated = True
            self.expression_mode = False  # Сбрасываем режим выражений
            self.update_display()

        except Exception as e:
            self.display.setText("Ошибка")
            self.add_to_history(f"Ошибка в {func}: {str(e)}")

    def special_function(self, func):
        try:
            value = float(self.current_input)

            if func == "1/x":
                result = 1 / value if value != 0 else float("inf")
            elif func == "n!":
                result = (
                    math.factorial(int(value))
                    if value >= 0 and value == int(value)
                    else float("nan")
                )

            self.add_to_history(f"{func}({self.current_input}) = {result}")
            self.current_input = str(result)
            self.result_calculated = True
            self.expression_mode = False  # Сбрасываем режим выражений
            self.update_display()

        except Exception as e:
            self.display.setText("Ошибка")
            self.add_to_history(f"Ошибка в {func}: {str(e)}")

    def input_constant(self, const):
        constants = {"π": str(math.pi), "e": str(math.e)}
        self.current_input = constants[const]
        self.result_calculated = True
        self.expression_mode = False  # Сбрасываем режим выражений
        self.update_display()

    def change_angle_mode(self, mode):
        self.angle_mode = mode
        self.angle_label.setText(f"Углы: {self.angle_mode}")

    def memory_operation(self, op):
        try:
            value = float(self.current_input)

            if op == "MS":  # Memory Store
                self.memory = value
                self.add_to_history(f"Память сохранена: {value}")
            elif op == "MR":  # Memory Recall
                self.current_input = str(self.memory)
                self.result_calculated = True
                self.expression_mode = False  # Сбрасываем режим выражений
            elif op == "M+":  # Memory Add
                self.memory += value
                self.add_to_history(f"Память +{value} = {self.memory}")
            elif op == "M-":  # Memory Subtract
                self.memory -= value
                self.add_to_history(f"Память -{value} = {self.memory}")
            elif op == "MC":  # Memory Clear
                self.memory = 0
                self.add_to_history("Память очищена")

            self.memory_label.setText(f"M: {self.memory}")
            self.update_display()

        except Exception as e:
            self.display.setText("Ошибка")
            self.add_to_history(f"Ошибка памяти: {str(e)}")

    def percentage_operation(self):
        """Вычисление процента от числа"""
        if not self.previous_input:
            # Если нет предыдущего числа, просто делим на 100
            try:
                value = float(self.current_input)
                result = value / 100
                self.add_to_history(f"{self.current_input}% = {result}")
                self.current_input = str(result)
                self.result_calculated = True
                self.expression_mode = False  # Сбрасываем режим выражений
                self.update_display()
            except Exception as e:
                self.display.setText("Ошибка")
                self.add_to_history(f"Ошибка в %: {str(e)}")
        else:
            # Вычисляем процент от предыдущего числа
            try:
                base_number = float(self.previous_input)
                percentage = float(self.current_input)
                result = (percentage / 100) * base_number

                # Добавляем в историю с понятным форматом
                self.add_to_history(f"{percentage}% от {base_number} = {result}")

                self.current_input = str(result)
                self.operation = ""
                self.previous_input = ""
                self.result_calculated = True
                self.expression_mode = False  # Сбрасываем режим выражений
                self.update_display()

            except Exception as e:
                self.display.setText("Ошибка")
                self.add_to_history(f"Ошибка вычисления %: {str(e)}")

    def toggle_sign(self):
        if self.current_input != "0":
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
            self.update_display()

    def backspace(self):
        """Удаление последнего символа"""
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = "0"
            self.operation = ""
            self.previous_input = ""
            self.expression_mode = False
        self.update_display()

    def clear(self):
        self.current_input = "0"
        self.previous_input = ""
        self.operation = ""
        self.result_calculated = False
        self.expression_mode = False  # Сбрасываем режим выражений
        self.update_display()

    def update_display(self):
        # Форматирование больших чисел
        try:
            num = float(self.current_input)
            if abs(num) >= 1e10 or (abs(num) < 1e-4 and num != 0):
                formatted = f"{num:.6e}"
            else:
                formatted = f"{num:g}"
            self.display.setText(formatted)
        except:
            self.display.setText(self.current_input)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_input)
        self.add_to_history(f"Скопировано в буфер: {self.current_input}")

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text().strip()

        if not clipboard_text:
            self.show_message("Буфер обмена пуст!")
            return

        try:
            # Пытаемся преобразовать в число
            # Сначала пробуем float, затем int
            if "." in clipboard_text or "e" in clipboard_text.lower():
                number = float(clipboard_text)
            else:
                number = int(clipboard_text)

            # Устанавливаем значение
            self.current_input = str(number)
            self.result_calculated = True
            self.expression_mode = False
            self.update_display()
            self.add_to_history(f"Вставлено из буфера: {number}")

        except ValueError:
            self.show_message(f"Не удалось преобразовать '{clipboard_text}' в число!")

    def show_message(self, message):
        """Показать сообщение пользователю"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Уведомление")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4dbef9;
            }
        """)
        msg_box.exec()

    def toggle_history(self):
        """Переключить видимость истории"""
        self.history_visible = not self.history_visible
        self.history_widget.setVisible(self.history_visible)

        if self.history_visible:
            # self.toggle_history_btn.setText("Скрыть историю")
            self.toggle_history_btn.setIcon(QIcon(os.path.join("img", "history0.png")))
            # Расширяем окно при показе истории
            self.setFixedSize(650, 700)
        else:
            # self.toggle_history_btn.setText("Показать историю")
            self.toggle_history_btn.setIcon(QIcon(os.path.join("img", "history.png")))
            # Возвращаем исходный размер при скрытии истории
            self.setFixedSize(400, 700)

    def add_to_history(self, entry):
        self.history.append(entry)
        self.history_display.append(entry)

        # Ограничиваем историю последними 100 записями
        if len(self.history) > 100:
            self.history.pop(0)

    def clear_history(self):
        self.history.clear()
        self.history_display.clear()

    def show_help(self):
        """Показать окно справки"""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Справка по калькулятору")
        help_dialog.setFixedSize(700, 600)
        help_dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)

        layout = QVBoxLayout()
        help_dialog.setLayout(layout)

        # Создаем прокручиваемую область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)

        help_text = """
<h2 style="color: #3daee9; margin-bottom: 20px;">📖 Справка по инженерному калькулятору</h2>

<h3 style="color: #ff9500; margin-top: 20px;">💰 Работа с процентами</h3>
<p><strong>Способ 1: Процент от числа</strong></p>
<ul>
<li>Введите базовое число (например, 78)</li>
<li>Нажмите любую операцию (+, -, ×, ÷)</li>
<li>Введите процентное значение (например, 13)</li>
<li>Нажмите % для получения результата</li>
<li>Пример: 78 + 13 % = 10.14 (13% от 78)</li>
</ul>

<p><strong>Способ 2: Простое преобразование</strong></p>
<ul>
<li>Введите число (например, 0.25)</li>
<li>Нажмите % для получения 0.0025</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">🔢 Тригонометрические функции</h3>
<p><strong>Основные функции:</strong></p>
<ul>
<li><strong>sin, cos, tan</strong> - прямые тригонометрические функции</li>
<li><strong>asin, acos, atan</strong> - обратные тригонометрические функции</li>
<li>Переключение между градусами (DEG), радианами (RAD) и градами (GRAD)</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">📈 Логарифмы и экспоненты</h3>
<ul>
<li><strong>ln</strong> - натуральный логарифм</li>
<li><strong>log</strong> - десятичный логарифм</li>
<li><strong>eˣ</strong> - экспонента (e в степени x)</li>
<li><strong>10ˣ</strong> - 10 в степени x</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">⚡ Степени и корни</h3>
<ul>
<li><strong>x²</strong> - квадрат числа</li>
<li><strong>x³</strong> - куб числа</li>
<li><strong>xʸ</strong> - возведение в произвольную степень</li>
<li><strong>√</strong> - квадратный корень</li>
<li><strong>∛</strong> - кубический корень</li>
<li><strong>ʸ√x</strong> - корень произвольной степени</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">🧮 Специальные функции</h3>
<ul>
<li><strong>1/x</strong> - обратное число</li>
<li><strong>n!</strong> - факториал (только для целых положительных чисел)</li>
<li><strong>±</strong> - смена знака</li>
<li><strong>π</strong> - число Пи (3.14159...)</li>
<li><strong>e</strong> - число Эйлера (2.71828...)</li>
<li><strong>2nd</strong> - переключение на вторичные функции кнопок</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">🔄 Функция 2nd</h3>
<p><strong>Как использовать:</strong></p>
<ul>
<li>Нажмите кнопку <strong>2nd</strong> - она подсветится оранжевым</li>
<li>Затем нажмите нужную функцию для получения альтернативного результата</li>
<li>Режим автоматически отключится после использования</li>
</ul>

<p><strong>Доступные альтернативы:</strong></p>
<ul>
<li><strong>2nd + sin</strong> = asin (арксинус)</li>
<li><strong>2nd + cos</strong> = acos (арккосинус)</li>
<li><strong>2nd + tan</strong> = atan (арктангенс)</li>
<li><strong>2nd + ln</strong> = eˣ (экспонента)</li>
<li><strong>2nd + log</strong> = 10ˣ (10 в степени x)</li>
<li><strong>2nd + x²</strong> = √ (квадратный корень)</li>
<li><strong>2nd + x³</strong> = ∛ (кубический корень)</li>
</ul>

<p><strong>Примеры использования вторичных функций:</strong></p>
<ul>
<li><strong>Найти угол по синусу:</strong> Введите 0.5 → 2nd → sin = 30° (в режиме DEG)</li>
<li><strong>Найти угол по косинусу:</strong> Введите 0.707 → 2nd → cos ≈ 45°</li>
<li><strong>Найти угол по тангенсу:</strong> Введите 1 → 2nd → tan = 45°</li>
<li><strong>Экспонента:</strong> Введите 2 → 2nd → ln = e² ≈ 7.389</li>
<li><strong>Степень 10:</strong> Введите 3 → 2nd → log = 10³ = 1000</li>
<li><strong>Квадратный корень:</strong> Введите 25 → 2nd → x² = √25 = 5</li>
<li><strong>Кубический корень:</strong> Введите 27 → 2nd → x³ = ∛27 = 3</li>
</ul>

<p><strong>Последовательность действий:</strong></p>
<ol>
<li>Введите число на дисплей</li>
<li>Нажмите кнопку <strong>2nd</strong> (она подсветится оранжевым)</li>
<li>Нажмите нужную функцию (sin, cos, tan, ln, log, x², x³)</li>
<li>Получите результат альтернативной функции</li>
<li>Режим 2nd автоматически отключится</li>
</ol>

<h3 style="color: #ff9500; margin-top: 20px;">💾 Работа с памятью</h3>
<ul>
<li><strong>MS</strong> - сохранить в память</li>
<li><strong>MR</strong> - вызвать из памяти</li>
<li><strong>M+</strong> - добавить к памяти</li>
<li><strong>M-</strong> - вычесть из памяти</li>
<li><strong>MC</strong> - очистить память</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">⌨️ Горячие клавиши</h3>
<ul>
<li><strong>0-9</strong> - ввод цифр</li>
<li><strong>+ - * /</strong> - основные операции</li>
<li><strong>( )</strong> - скобки для выражений</li>
<li><strong>Enter/Return</strong> - вычислить результат</li>
<li><strong>Backspace</strong> - удалить последний символ</li>
<li><strong>Delete/Escape</strong> - очистить все</li>
<li><strong>Ctrl+C</strong> - копировать результат</li>
<li><strong>Ctrl+V</strong> - вставить число из буфера</li>
<li><strong>F1</strong> - показать эту справку</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">📋 Буфер обмена</h3>
<ul>
<li><strong>Копировать</strong> - скопировать результат в буфер</li>
<li><strong>Вставить</strong> - вставить число из буфера с автоматическим преобразованием</li>
<li>Поддерживает целые числа, дробные и в научной нотации</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">📊 История вычислений</h3>
<ul>
<li>Автоматическое ведение истории всех операций</li>
<li>Возможность показать/скрыть панель истории</li>
<li>Очистка истории одним нажатием</li>
<li>Ограничение: последние 100 операций</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">🔧 Работа со скобками</h3>
<p><strong>Создание выражений:</strong></p>
<ul>
<li>Нажимайте кнопки ( и ) для создания сложных выражений</li>
<li>Автоматическое добавление знака умножения: 2( → 2×(</li>
<li>Проверка соответствия открывающих и закрывающих скобок</li>
<li>Поддержка вложенных скобок: ((2+3)×4)+1</li>
</ul>

<p><strong>Примеры выражений:</strong></p>
<ul>
<li><strong>Простые:</strong> (2+3)×4 = 20</li>
<li><strong>Вложенные:</strong> ((5+3)×2)+1 = 17</li>
<li><strong>Сложные:</strong> (10+5)/(3-1) = 7.5</li>
<li><strong>Со скобками:</strong> 2×(3+4×(5-2)) = 34</li>
</ul>

<p><strong>Особенности:</strong></p>
<ul>
<li>Полное вычисление выражения при нажатии =</li>
<li>Проверка корректности скобок перед вычислением</li>
<li>Поддержка приоритета операций</li>
<li>Безопасный парсер без использования eval()</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">🎯 Режимы работы</h3>
<p><strong>Обычный режим:</strong></p>
<ul>
<li>Простые операции: 5 + 3 = 8</li>
<li>Пошаговое вычисление</li>
<li>Работает как стандартный калькулятор</li>
</ul>

<p><strong>Режим выражений:</strong></p>
<ul>
<li>Автоматически активируется при использовании скобок</li>
<li>Поддерживает сложные выражения: 11-(5+5) = 1</li>
<li>Правильный приоритет операций</li>
<li>Полное вычисление при нажатии =</li>
</ul>

<h3 style="color: #ff9500; margin-top: 20px;">🎨 Интерфейс</h3>
<ul>
<li>Темная профессиональная тема</li>
<li>Цветовая кодировка кнопок по типу функций</li>
<li>Научная нотация для больших и малых чисел</li>
<li>Информативные сообщения об ошибках</li>
</ul>

<p style="margin-top: 30px; text-align: center; color: #888888;">
<em>Версия 2.0 - Профессиональный инженерный калькулятор с поддержкой выражений</em>
</p>
        """

        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 12px;
                line-height: 1.6;
                padding: 20px;
            }
        """)
        help_label.setTextFormat(Qt.TextFormat.RichText)

        content_layout.addWidget(help_label)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(help_dialog.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4dbef9;
            }
        """)
        layout.addWidget(close_btn)

        help_dialog.exec()

    def toggle_second_mode(self):
        """Переключить режим 2nd функций"""
        self.second_mode = not self.second_mode

        if self.second_mode:
            # Активируем режим 2nd - подсвечиваем кнопку
            self.second_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b35;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #ff8555;
                }
                QPushButton:pressed {
                    background-color: #dd5520;
                }
            """)
            self.add_to_history("Режим 2nd активирован")
        else:
            # Деактивируем режим 2nd - возвращаем обычный стиль
            self.second_btn.setStyleSheet("""
                QPushButton {
                    background-color: #505050;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #606060;
                }
                QPushButton:pressed {
                    background-color: #707070;
                }
            """)
            self.add_to_history("Режим 2nd деактивирован")

    def reset_second_mode(self):
        """Сбросить режим 2nd после использования"""
        if self.second_mode:
            self.second_mode = False
            self.second_btn.setStyleSheet("""
                QPushButton {
                    background-color: #505050;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #606060;
                }
                QPushButton:pressed {
                    background-color: #707070;
                }
            """)


def main():
    app = QApplication(sys.argv)
    #app.setStyle("Fusion")

    # Темная тема
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(64, 64, 64))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(61, 174, 233))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(61, 174, 233))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    calculator = EngineeringCalculator()
    calculator.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
