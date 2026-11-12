# main.py

def show_menu():
    """메뉴 화면을 출력한다. (반환값 없음)"""
    print("=" * 40)
    print("        나만의 퀴즈 게임")
    print("=" * 40)
    print("1. 퀴즈 풀기")
    print("2. 퀴즈 추가")
    print("3. 퀴즈 목록")
    print("4. 점수 확인")
    print("5. 종료")
    print("=" * 40)


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


def play_quiz():
    print("준비 중입니다.")


def add_quiz():
    print("준비 중입니다.")


def list_quizzes():
    print("준비 중입니다.")


def show_score():
    print("준비 중입니다.")


def main():
    """메뉴를 반복해서 보여 주고, 고른 번호에 맞는 기능을 실행한다. 5를 고르면 끝낸다."""
    try:
        while True:
            show_menu()
            choice = read_number("선택: ", 1, 5)

            if choice == 1:
                play_quiz()
            elif choice == 2:
                add_quiz()
            elif choice == 3:
                list_quizzes()
            elif choice == 4:
                show_score()
            else:                             # 5번: 종료
                print("프로그램을 종료합니다.")
                break
    except (KeyboardInterrupt, EOFError):     # Ctrl+C 또는 입력 스트림 종료
        print("\n입력이 중단되어 안전하게 종료합니다.")


if __name__ == "__main__":
    main()