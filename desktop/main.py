import random
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QVBoxLayout,
                             QWidget)


class SeoMcpAgent(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):

        # Main layout
        self.main_layout = QVBoxLayout()
        

        # entering URL for analyze

        self.url_layout = QHBoxLayout()

        self.url_label_1 = QLabel("Analyze your website for SEO opportunities")
        self.url_label_1.setFont(QFont("Arial", 12, QFont.Weight.Bold, QFont.Style.StyleNormal))
        self.url_layout.addWidget(self.url_label_1)

        self.url_label_2 = QLabel("Enter url:")
        self.url_label_2.setFont(QFont("Arial", 16, QFont.Weight.Bold, QFont.Style.StyleItalic))
        self.url_label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_layout.addWidget(self.url_label_2)

       


        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter url")
        self.url_input.setFixedWidth(400)
        self.url_input.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.url_layout.addWidget(self.url_input)

        # Checkbox widget

        self.top_layout = QHBoxLayout()
        # score top layout
        self.score_top_layout = QHBoxLayout()
        self.score_top_layout.setContentsMargins(0, 0, 0, 0)
        self.score_top_layout.setSpacing(0)
        self.game_score = QLabel(f"Game score: 0 : 0")
        self.game_score.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.game_score.setStyleSheet("color: red;")
        self.game_score.setAlignment(Qt.AlignCenter)
        self.score_top_layout.addWidget(self.game_score)

        # Левый верхний блок (3 элемента)
        self.left_top_layout = QVBoxLayout()
        self.left_top_layout.setContentsMargins(0, 0, self.width() // 2, 0)

        # Player 1 name
        self.label_username_1 = QLabel("Player 1:")
        self.label_username_1.setFont(QFont("Arial", 16, QFont.Bold))
        self.label_username_1.setAlignment(Qt.AlignCenter)
        self.left_top_layout.addWidget(self.label_username_1)

        # Edit widget for player 1 name
        self.user_name_1_edit = QLineEdit()
        self.user_name_1_edit.setPlaceholderText("Enter your name")
        self.user_name_1_edit.setFixedWidth(200)
        self.left_top_layout.addWidget(self.user_name_1_edit)

        # enter button layout
        self.enter_button_layout = QHBoxLayout()
        self.enter_button_layout.setContentsMargins(250, 0, 300, 0)
        self.enter_button_layout.setStretchFactor(self.enter_button_layout, 1)
        # self.enter_button_layout.setSpacing(0)
        self.enter_button_layout.addStretch(1)


        # "Enter" button for confirming name
        self.enter_button = QPushButton("Make cool!")
        self.enter_button.setFixedSize(200, 40)
        self.enter_button.clicked.connect(self.confirm_name)
        self.enter_button_layout.addWidget(self.enter_button, alignment=Qt.AlignCenter | Qt.AlignTop)

        # Total score label 1
        self.total_score_label_1 = QLabel(f"Total score: {1}")
        self.total_score_label_1.setFont(QFont("Arial", 14, QFont.Bold))
        self.left_top_layout.addWidget(self.total_score_label_1)

        # current score 1
        self.current_count_label_1 = QLabel(f"Current score: {1}")
        self.current_count_label_1.setFont(QFont("Arial", 14, QFont.Bold))
        self.left_top_layout.addWidget(self.current_count_label_1)
        self.left_top_layout.addStretch(1)

        # Правый верхний блок (3 элемента)
        self.right_top_layout = QVBoxLayout()

        # Player 2 name
        self.label_username_2 = QLabel("Player 2:")
        self.label_username_2.setFont(QFont("Arial", 16, QFont.Bold))
        self.label_username_2.setAlignment(Qt.AlignCenter)
        self.right_top_layout.addWidget(self.label_username_2)

        # Edit widget for player 2 name
        self.user_name_2_edit = QLineEdit()
        self.user_name_2_edit.setPlaceholderText("Enter your name")
        self.user_name_2_edit.setFixedWidth(200)
        self.right_top_layout.addWidget(self.user_name_2_edit)

        # Total score label 2
        self.total_score_label_2 = QLabel(f"Total score: {2}")
        self.total_score_label_2.setFont(QFont("Arial", 14, QFont.Bold))
        self.right_top_layout.addWidget(self.total_score_label_2)

        # current score 2
        self.current_count_label_2 = QLabel(f"Current score: {1}")
        self.current_count_label_2.setFont(QFont("Arial", 14, QFont.Bold))
        self.right_top_layout.addWidget(self.current_count_label_2)
        self.right_top_layout.addStretch(1)

        # Добавляем два верхних блока в общий горизонтальный слой

        self.top_layout.addLayout(self.left_top_layout)
        self.top_layout.addLayout(self.right_top_layout)

        # Нижний блок (3 элемента в один ряд)
        self.dices_bottom_layout = QHBoxLayout()
        self.set_dices()

        # Добавляем все в основной слой
        self.main_layout.addLayout(self.url_layout)
        self.main_layout.addLayout(self.score_top_layout)
        self.main_layout.addLayout(self.top_layout, 1)  # Верхний блок (50%)
        self.main_layout.addLayout(self.enter_button_layout, 1)
        self.main_layout.addLayout(self.dices_bottom_layout, 1)  # Нижний блок (50%)
        # self.main_layout.addLayout(self.roll_layout, 1)  # Кнопка "ROLL DICE" (50%)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Seo MCP agent")
        self.resize(800, 600)  # Размер окна

        # Connect the return pressed event to confirm name
        self.user_name_1_edit.returnPressed.connect(self.confirm_name)
        self.user_name_1_edit.textChanged.connect(self.update_label)
        return

    def roll_button(self):
        # Add ROLL button
        self.roll_layout = QHBoxLayout()
        self.roll_button = QPushButton("ROLL DICE")
        self.roll_button.setFixedSize(200, 50)
        self.roll_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.roll_layout.addWidget(self.roll_button, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.main_layout.addLayout(self.roll_layout, 1)  # Кнопка "ROLL DICE" (50%)

    def save_button(self):
        # Save count button
        self.save_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.setFixedSize(100, 40)
        self.save_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.save_button.clicked.connect(self.save_score)
        self.save_layout.addWidget(self.save_button, alignment=Qt.AlignHCenter | Qt.AlignTop)
        self.main_layout.addLayout(self.save_layout, 1)  # Кнопка "SAVE" (50%)

    def set_dices(self, count=5):
        self.dice_labels = []
        # dice_layout = QHBoxLayout()
        for _ in range(count):  # Assuming 5 dice
            dice_label = QLabel("0")
            dice_label.setFont(QFont("Arial", 24, QFont.Bold))
            dice_label.setAlignment(Qt.AlignCenter)
            dice_label.setFixedSize(50, 50)
            dice_label.setEnabled(True)
            self.dices_bottom_layout.addWidget(dice_label)
            self.dice_labels.append(dice_label)
        # self.layout.addLayout(dice_layout)

    def update_label(self, text):
        self.label_username_1.setText(f"Your name: {text}")

    def confirm_name(self):
        # Get the player name from the input field
        self.player_name_1 = self.user_name_1_edit.text()
        self.player_name_2 = self.user_name_2_edit.text()

        if not self.player_name_1 or not self.player_name_2:
            QMessageBox.warning(self, "Warning", "Please enter your name!")
            return

        # Remove the input field and enter button
        self.user_name_1_edit.setParent(None)
        self.user_name_2_edit.setParent(None)
        self.enter_button.setParent(None)

        # Update the label
        self.label_username_1.setText(f"Player 1: {self.player_name_1}")
        self.label_username_1.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_username_2.setText(f"Player 2: {self.player_name_2}")
        self.label_username_2.setFont(QFont("Arial", 14, QFont.Bold))

        self.roll_button()
        # Add START button
        self.start_button = QPushButton("START GAME")
        self.start_button.setFixedSize(200, 50)
        self.start_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.start_button.clicked.connect(self.start_game)

        # # Add stretch to push the start button to the middle and top
        # self.bottom_layout.addStretch(1)
        self.roll_layout.addWidget(self.start_button, alignment=Qt.AlignHCenter | Qt.AlignTop)

    def start_game(self):
        self.roll_button.clicked.connect(self.roll_dice)
        self.roll_button.setStyleSheet("background-color: blue; color: white;")

        self.start_button.setParent(None)
        self.save_button()
        self.turn_marker()

    def turn_marker(self):
        if self.turn == 1:
            self.label_username_1.setStyleSheet("background-color: green; color: white;")
            self.label_username_2.setStyleSheet("")
        else:
            self.label_username_2.setStyleSheet("background-color: green; color: white;")
            self.label_username_1.setStyleSheet("")

    def roll_dice(self):
        # Roll all enabled dice
        if self.current_count > 0 and len([dice for dice in self.dice_labels if dice.isEnabled()]) == 0:
            self.reset_dices()
        for dice_label in self.dice_labels:
            if dice_label.isEnabled():
                dice_label.setText(str(random.randint(1, 6)))
                dice_label.setStyleSheet("")  # Reset styling
                # dice_label.setEnabled(True)  # Reset enabled state
        enabled_dices = [dice for dice in self.dice_labels if dice.isEnabled()]
        res = [dice.text() for dice in enabled_dices]
        print(res)
        # Get result from DiceUtils
        result = DiceUtils(enabled_dices).count_dice()
        score = result[0]
        kept_dice_dict = result[1]  # Dict of dice to KEEP

        # Disable all dice EXCEPT those in the kept_dice_dict
        # Track the number of each value we want to keep
        to_keep = kept_dice_dict.copy()

        # Process each die
        for dice_label in self.dice_labels:
            value = dice_label.text()

            # If this die value is in our "keep" list and we still need more of this value
            if value in to_keep and to_keep[value] > 0:
                # Keep this die (leave enabled)
                to_keep[value] -= 1
            else:
                # Disable this die (it's not needed for scoring)
                dice_label.setStyleSheet("background-color: lightgray; color: gray;")
                dice_label.setEnabled(False)

        # Show result message
        player = self.player_name_1 if self.turn == 1 else self.player_name_2
        message = f"{player}, You rolled {score}." if score > 0 else f"{player}, You rolled nothing."
        QMessageBox.information(
            self,
            "Your turn",
            message,
        )

        # Store the current score
        self.current_count += score

        if self.turn == 1:
            self.current_count_label_1.setText(f"Current count: {self.current_count}")
        else:
            self.current_count_label_2.setText(f"Current count: {self.current_count}")
        if score == 0:
            self.turn = 2 if self.turn == 1 else 1
            QMessageBox.information(
                self,
                "Change turn",
                "You rolled nothing. Change turn",
            )
            self.turn_marker()
            self.reset_dices()
            self.current_count = 0
            self.clear_current_count_label()
        # self.free_dices = 5 - len(kept_dice_dict)

    def clear_current_count_label(self):
        self.current_count_label_1.setText(f"Current count: {self.current_count}")
        self.current_count_label_2.setText(f"Current count: {self.current_count}")    

    def reset_dices(self):
        for dice_label in self.dice_labels:
            dice_label.setEnabled(True)
            dice_label.setStyleSheet("")  # Reset styling

    def save_score(self):
        # To be implemented in the next step
        if self.turn == 1:
            self.total_score_1 += self.current_count
            self.total_score_label_1.setText(f"Total score: {self.total_score_1}")
        else:
            self.total_score_2 += self.current_count
            self.total_score_label_2.setText(f"Total score: {self.total_score_2}")
        self.current_count = 0
        self.turn = 2 if self.turn == 1 else 1
        QMessageBox.information(
            self,
            "Change turn",
            "Score saved. Change turn",
        )
        self.turn_marker()
        self.reset_dices()
        self.clear_current_count_label()
        self.check_winner()

    def check_winner(self):
        if self.total_score_1 >= 200:
            QMessageBox.information(
                self,
                "Winner",
                f"{self.player_name_1} wins!",
            )
            self.game_score_1 += 1
            self.game_score.setText(f"Game score: {self.game_score_1} : {self.game_score_2}")
            self.reset_dices()
            self.clear_current_count_label()
            self.clear_total_count()
            # self.close()
        elif self.total_score_2 >= 200:
            QMessageBox.information(
                self,
                "Winner",
                f"{self.player_name_2} wins!",
            )
            # self.close()
            self.game_score_2 += 1
            self.game_score.setText(f"Game score: {self.game_score_1} : {self.game_score_2}")
            self.reset_dices()
            self.clear_current_count_label()
            self.clear_total_count()

    def clear_total_count(self):
        self.total_score_1 = 0
        self.total_score_2 = 0
        self.total_score_label_1.setText(f"Total score: {self.total_score_1}")
        self.total_score_label_2.setText(f"Total score: {self.total_score_2}")  
        
        # if hasattr(self, "Total_score_label"):
        #     self.total_score_label.setText(f"Total score: {self.total_score}")
        # else:
        #     self.total_score_label = QLabel(f"Total: {self.total_score}")
        #     self.total_score_label.setFont(QFont("Arial", 14, QFont.Bold))
        #     self.layout.addWidget(self.total_score_label)

    def _dice_counter(self, dice):
        count = 0
        # check if all dice are the same
        if len(set(dice)) == 1:
            if dice[0].text() == "1":
                return 1000
            return int(dice[0].text() * 30)
        # Check if 4s
        if len(set(dice)) == 2:
            if dice[0].text() == dice[1].text():
                if dice[0].text() == "1":
                    return 2000
                return int(dice[0].text()) * 200
        # count 5s
        count += sum(5 for d in dice if d.text() == "5")
        # count 10
        count += sum(10 for d in dice if d.text() == "1")
        return count

    def _dict_dice(self):
        dice_dict = {}
        for dice in self.dice_labels:
            dice_dict[dice.text()] = dice_dict.get(dice.text(), 0) + 1
        return dice_dict


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SeoMcpAgent()
    window.show()
    sys.exit(app.exec_())
