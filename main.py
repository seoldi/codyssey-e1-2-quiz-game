# main.py
"""나만의 퀴즈 게임 (터미널 · 표준 라이브러리만 사용)"""

import json
import os
from pathlib import Path

# 데이터 파일: 프로젝트 루트(이 파일이 있는 폴더)의 state.json, UTF-8
STATE_FILE = Path(__file__).resolve().parent / "state.json"


class Quiz:
    """퀴즈 한 문제를 표현한다. 문제, 선택지 4개, 정답 번호(1~4)를 가진다."""

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices      # 선택지 문자열 4개의 리스트
        self.answer = answer        # 정답 번호 (1~4)

    def show(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        title = f"[문제 {number}]" if number is not None else "[문제]"
        print(title)
        print(self.question)
        print()
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")

    def is_correct(self, choice):
        """사용자가 고른 번호가 정답이면 True."""
        return choice == self.answer

    def to_dict(self):
        """JSON으로 저장하기 위해 딕셔너리로 바꾼다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 Quiz를 만든다. 형식이 맞지 않으면 ValueError."""
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제가 올바르지 않습니다.")
        if (not isinstance(choices, list) or len(choices) != 4
                or not all(isinstance(c, str) for c in choices)):
            raise ValueError("선택지는 문자열 4개여야 합니다.")
        if isinstance(answer, bool) or not isinstance(answer, int) or not 1 <= answer <= 4:
            raise ValueError("정답 번호는 1~4 사이 정수여야 합니다.")
        return cls(question, choices, answer)


def create_default_quizzes():
    """기본 퀴즈 데이터. 주제: Git · Docker · 터미널 기초 (E1-1 복습)"""
    return [
        Quiz("변경 내용을 '내 컴퓨터'에 버전으로 기록하는 Git 명령은?",
             ["git push", "git commit", "git clone", "git pull"], 2),
        Quiz("컨테이너를 삭제해도 데이터가 남게 하려면 무엇을 연결해야 할까?",
             ["EXPOSE", "COPY", "볼륨(volume)", "환경변수"], 3),
        Quiz("docker run -p 8080:80 에서 8080은 무엇의 포트인가?",
             ["호스트(내 컴퓨터)의 포트", "컨테이너 안의 포트", "이미지 버전", "프로세스 번호"], 1),
        Quiz("chmod 755 가 의미하는 권한 표기는?",
             ["rw-r--r--", "rwx------", "rw-------", "rwxr-xr-x"], 4),
        Quiz("Git과 GitHub의 관계로 옳은 것은?",
             ["GitHub는 내 컴퓨터에 설치하는 버전 관리 도구다",
              "Git은 인터넷 서비스이고 GitHub는 프로그램이다",
              "GitHub는 Git 기록을 올려 두고 협업하는 원격 서비스다",
              "둘은 완전히 같은 것이다"], 3),
        Quiz("이미지를 실행한 것을 무엇이라고 부를까?",
             ["컨테이너", "Dockerfile", "볼륨", "레지스트리"], 1),
        Quiz("리눅스에서 '한 단계 위 폴더'를 가리키는 상대 경로 기호는?",
             [".", "~", "/", ".."], 4),
        Quiz("원격 저장소를 처음 통째로 내 컴퓨터로 받아 오는 명령은?",
             ["git pull", "git add", "git clone", "git init"], 3),
    ]


def read_number(prompt, min_value, max_value):
    """
    prompt를 보여 주고 min_value~max_value 사이의 정수를 입력받아 돌려준다.
    올바른 값이 들어올 때까지 안내 메시지를 내고 다시 묻는다.
    """
    while True:
        text = input(prompt).strip()          # 앞뒤 공백 제거

        if text == "":                        # 빈 입력 (그냥 Enter)
            print("⚠ 아무것도 입력하지 않았습니다. 숫자를 입력하세요.")
            continue

        try:
            number = int(text)                # 숫자 변환 시도
        except ValueError:                    # abc 같은 숫자가 아닌 입력
            print("⚠ 숫자만 입력할 수 있습니다.")
            continue

        if number < min_value or number > max_value:   # 범위 밖
            print(f"⚠ {min_value}~{max_value} 사이의 숫자를 입력하세요.")
            continue

        return number                         # 모두 통과 → 값을 돌려주고 종료


def read_text(prompt):
    """비어 있지 않은 문자열을 입력받아 돌려준다. (앞뒤 공백 제거, 빈 입력이면 다시 묻기)"""
    while True:
        text = input(prompt).strip()
        if text == "":
            print("⚠ 아무것도 입력하지 않았습니다. 다시 입력하세요.")
            continue
        return text


class QuizGame:
    """게임 전체를 관리한다. 퀴즈 목록과 최고 점수를 속성으로 가진다."""

    def __init__(self, state_file=STATE_FILE):
        self.state_file = Path(state_file)
        self.quizzes = []
        self.best_score = None   # 아직 퀴즈를 풀지 않았으면 None
        self.load_state()

    def reset_to_default(self):
        """기본 퀴즈 데이터로 초기화한다."""
        self.quizzes = create_default_quizzes()
        self.best_score = None

    def load_state(self):
        """state.json에서 퀴즈와 최고 점수를 불러온다. 없거나 손상되어도 실행 가능해야 한다."""
        if not self.state_file.exists():              # 첫 실행: 파일이 없음
            self.reset_to_default()
            print("저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            best_score = data["best_score"]
            if best_score is not None and (isinstance(best_score, bool)
                                           or not isinstance(best_score, int)):
                raise ValueError("최고 점수는 정수 또는 null이어야 합니다.")
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError, ValueError):
            # 파일이 손상됨 → 안내하고 기본 데이터로 복구
            print("⚠ 데이터 파일이 손상되어 기본 퀴즈로 복구합니다.")
            self.reset_to_default()
            self.save_state()
        except OSError:
            print("⚠ 데이터 파일을 읽을 수 없어 기본 퀴즈로 시작합니다.")
            self.reset_to_default()
        else:
            self.quizzes = quizzes
            self.best_score = best_score
            score_text = "없음" if best_score is None else f"{best_score}점"
            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고 점수 {score_text})")

    def save_state(self):
        """퀴즈와 최고 점수를 state.json에 UTF-8로 저장한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }
        temp_file = self.state_file.with_name(self.state_file.name + ".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            os.replace(temp_file, self.state_file)    # 쓰기가 끝난 뒤에 교체 (중간에 끊겨도 안전)
        except OSError:
            print("⚠ 데이터 파일을 저장하지 못했습니다.")

    def show_menu(self):
        """메뉴 화면을 출력한다."""
        print("=" * 40)
        print("        나만의 퀴즈 게임")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def play_quiz(self):
        """
        저장된 퀴즈를 순서대로 출제하고 정답 여부를 알려 준 뒤 결과를 보여 준다.
        점수(100점 만점, 정수)를 돌려준다. 퀴즈가 없으면 None.
        """
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
            return None

        total = len(self.quizzes)
        correct = 0
        print(f"\n퀴즈를 시작합니다! (총 {total}문제)")
        for number, quiz in enumerate(self.quizzes, start=1):
            print("-" * 40)
            quiz.show(number)
            choice = read_number("정답 입력 (1~4): ", 1, 4)
            if quiz.is_correct(choice):
                correct += 1
                print("정답입니다!")
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")

        score = round(correct / total * 100)
        print("=" * 40)
        print(f"결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        print("=" * 40)
        return score

    def add_quiz(self):
        """새 퀴즈(문제, 선택지 4개, 정답 번호)를 입력받아 목록에 추가한다."""
        print("\n새로운 퀴즈를 추가합니다.")
        question = read_text("문제를 입력하세요: ")
        choices = [read_text(f"선택지 {i}: ") for i in range(1, 5)]
        answer = read_number("정답 번호 (1~4): ", 1, 4)

        self.quizzes.append(Quiz(question, choices, answer))
        self.save_state()
        print(f"퀴즈가 추가되었습니다! (총 {len(self.quizzes)}개)")

    def list_quizzes(self):
        """등록된 퀴즈의 문제 목록을 보여 준다."""
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print("-" * 40)

    def update_best_score(self, score):
        """이번 점수가 최고 점수보다 높으면 갱신하고 안내한다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.save_state()
            print("새로운 최고 점수입니다!")

    def show_score(self):
        """최고 점수를 보여 준다."""
        if self.best_score is None:
            print("아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어 보세요.")
        else:
            print(f"최고 점수: {self.best_score}점")

    def run(self):
        """메뉴를 반복해서 보여 주고, 고른 번호에 맞는 기능을 실행한다. 5를 고르면 끝낸다."""
        try:
            while True:
                self.show_menu()
                choice = read_number("선택: ", 1, 5)

                if choice == 1:
                    score = self.play_quiz()
                    if score is not None:
                        self.update_best_score(score)
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_score()
                else:                         # 5번: 종료
                    print("프로그램을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):  # Ctrl+C 또는 입력 스트림 종료
            print("\n입력이 중단되어 안전하게 종료합니다.")
        finally:
            self.save_state()                  # 어떤 경로로 끝나든 가능한 범위에서 저장


def main():
    QuizGame().run()


if __name__ == "__main__":
    main()
