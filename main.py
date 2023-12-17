from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
import sys


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setGeometry(200, 200, 300, 500)
        self.mathematical_operations = "+-*/^."
        self.parentheses = "()"
        self.error_input = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # numbers input and output
        self.text_space = QTextEdit()
        self.text_space.setReadOnly(True)
        self.text_space.setFontPointSize(16)
        self.text_space.setText("0")
        main_layout.addWidget(self.text_space)

        button_layouts = [
            ("(", ")", "C", "Delete"),
            ("1/x", "^", "sqrt(x)", "/"),
            ("7", "8", "9", "*"),
            ("4", "5", "6", "-"),
            ("1", "2", "3", "+"),
            ("+/-", "0", ".", "=")
        ]

        for row_buttons in button_layouts:
            row_layout = QHBoxLayout()
            for button_text in row_buttons:
                button = QPushButton(button_text)
                row_layout.addWidget(button)
                if button_text.isdigit():
                    button.pressed.connect(lambda number=button_text: self.number_button_functionality(number))
                elif button_text in self.mathematical_operations:
                    button.pressed.connect(lambda operator=button_text: self.math_button_functionality(operator))
                elif button_text == ".":
                    button.pressed.connect(self.button_dot_functionality)
                elif button_text == "(":
                    button.pressed.connect(self.button_left_parenthesis_functionality)
                elif button_text == ")":
                    button.pressed.connect(self.button_right_parenthesis_functionality)
                elif button_text == "=":
                    button.pressed.connect(self.button_equals_functionality)
                elif button_text == "1/x":
                    button.pressed.connect(self.button_divide_by_x_functionality)
                elif button_text == "sqrt(x)":
                    button.pressed.connect(self.button_sqrt_functionality)
                elif button_text == "C":
                    button.pressed.connect(self.button_delete_functionality)
                elif button_text == "Delete":
                    button.pressed.connect(self.button_backspace_functionality)
                elif button_text == "+/-":
                    button.pressed.connect(self.button_change_sign_functionality)

            main_layout.addLayout(row_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # number buttons logic
    def number_button_functionality(self, number: str):
        contents = self.get_expression()
        self.text_space.setText(contents + number if contents != "0" else number)

    # math buttons functions
    def math_button_functionality(self, operator: str):
        contents = self.get_expression()
        # can't follow another mathematical operation
        self.text_space.setText(contents + operator if contents[-1] not in self.mathematical_operations else contents)

    def button_left_parenthesis_functionality(self):
        contents = self.get_expression()
        self.text_space.setText(contents + "(" if contents != "0" else "(")

    def button_right_parenthesis_functionality(self):
        contents = self.get_expression()
        # there can't be opening and closing parenthesis after each other
        # also, a closing parenthesis must follow an opening one
        self.text_space.setText(contents + ")" if "(" in contents and contents[-1] != "(" else contents)

    def button_equals_functionality(self):
        contents = self.get_expression()
        result = self.process_expression(contents)
        self.text_space.setText(str(result))

    def button_divide_by_x_functionality(self):
        contents = self.get_expression()
        number, new_contents = "", ""
        for i in range(-1, -len(contents) - 1, -1):
            if contents[i] in (self.mathematical_operations + self.parentheses):
                new_contents = contents[:i + 1]
                break
            number = contents[i] + number
        self.text_space.setText(new_contents + "1/" + number)

    def button_sqrt_functionality(self):
        contents = self.get_expression()
        self.text_space.setText(contents + "^0.5" if contents[-1] not in self.mathematical_operations else contents)

    # dot and change the sign
    def button_dot_functionality(self):
        contents = self.get_expression()
        # can't follow another mathematical operation
        self.text_space.setText(contents + "." if contents[-1] not in self.mathematical_operations else contents)

    def button_change_sign_functionality(self):
        contents = self.get_expression()
        number, new_contents = "", ""
        for i in range(-1, -len(contents) - 1, -1):
            if contents[i] in (self.mathematical_operations + self.parentheses):
                new_contents = contents[:i + 1]
                break
            number = contents[i] + number
        if not new_contents:
            self.text_space.setText("-" + number)
        elif new_contents[-1] == "(":
            self.text_space.setText(new_contents + "-" + number)
        else:
            self.text_space.setText(new_contents + "(-" + number)

    # delete and backspace buttons
    def button_delete_functionality(self):
        self.text_space.setText("0")

    def button_backspace_functionality(self):
        contents = self.get_expression()
        contents_new = contents[:-1]
        self.text_space.setText(contents_new if contents_new else "0")

    # processing keyboard presses
    def keyPressEvent(self, event):
        key = event.key()

        functionality_mapping = {
            Qt.Key_0: lambda: self.number_button_functionality("0"),
            Qt.Key_1: lambda: self.number_button_functionality("1"),
            Qt.Key_2: lambda: self.number_button_functionality("2"),
            Qt.Key_3: lambda: self.number_button_functionality("3"),
            Qt.Key_4: lambda: self.number_button_functionality("4"),
            Qt.Key_5: lambda: self.number_button_functionality("5"),
            Qt.Key_6: lambda: self.number_button_functionality("6"),
            Qt.Key_7: lambda: self.number_button_functionality("7"),
            Qt.Key_8: lambda: self.number_button_functionality("8"),
            Qt.Key_9: lambda: self.number_button_functionality("9"),
            Qt.Key_Escape: self.close,
            Qt.Key_Enter: self.button_equals_functionality
        }

        functionality = functionality_mapping.get(key)
        if functionality:
            functionality()

    # processing the expression
    def get_expression(self):
        if self.error_input:
            self.error_input = False
            return "0"
        return self.text_space.toPlainText()

    def is_float_or_int(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def process_expression(self, input_string):
        stack = []
        queue = []

        math = ("+", "-", "*", "/", "^")
        precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
        current_number = str()

        for i, element in enumerate(input_string):
            if element.isdigit() or element == ".":
                current_number += element
            elif element == "-" and (i == 0 or input_string[i - 1] == "("):
                current_number += "-"
            elif element in math:
                if current_number:
                    queue.append(current_number)
                    current_number = str()
                while stack and precedence.get(stack[-1], 0) >= precedence.get(element, 0):
                    queue.append(stack.pop())
                stack.append(element)
            elif element == "(":
                stack.append(element)
            elif element == ")":
                if current_number:
                    queue.append(current_number)
                    current_number = ""
                while stack[-1] != "(":
                    queue.append(stack.pop())
                stack.pop()

        if current_number:
            queue.append(current_number)

        while stack:
            queue.append(stack.pop())

        return self.process_rpn(queue)

    def process_rpn(self, queue):
        stack = []

        for token in queue:
            if self.is_float_or_int(token) or (token[0] == "-" and token[1:].isdigit()):
                stack.append(float(token))
            else:
                pair_numbers = (stack.pop(), stack.pop())
                if token == "+":
                    stack.append(pair_numbers[1] + pair_numbers[0])
                elif token == "-":
                    stack.append(pair_numbers[1] - pair_numbers[0])
                elif token == "*":
                    stack.append(pair_numbers[1] * pair_numbers[0])
                elif token == "/":
                    try:
                        stack.append(pair_numbers[1] / pair_numbers[0])
                    except ZeroDivisionError:
                        self.error_input = True
                        return "Can't divide by zero!"
                elif token == "^":
                    stack.append(pair_numbers[1] ** pair_numbers[0])
        try:
            if stack[-1] == int(stack[-1]):
                stack[-1] = int(stack[-1])
        except TypeError:
            self.error_input = True
            return "Complex numbers aren't supported yet!"

        return stack[-1] if stack else 0


def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


def main():
    window()


if __name__ == '__main__':
    main()
