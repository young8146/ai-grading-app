import re
import streamlit as st

st.set_page_config(
    page_title="서논술형 자동 채점",
    page_icon="📝",
    layout="wide"
)

# ============================================================
# 공통 함수
# ============================================================

def norm(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[.,!?·:;()\[\]{}\"'“”‘’]", "", text)
    return text


def detect_method_label(text):
    t = norm(text)
    labels = {
        "정의": ["정의"],
        "예시": ["예시"],
        "인과": ["인과"],
        "분석": ["분석"],
        "비교와 대조": ["비교와대조", "비교대조"],
        "분류와 구분": ["분류와구분", "분류구분"],
    }
    return [name for name, words in labels.items() if any(w in t for w in words)]


def method_realized(text, method):
    t = norm(text)

    if method == "정의":
        return bool(re.search(r"(란|이란|뜻한다|말한다|의미한다|이다)", t))

    if method == "예시":
        return bool(re.search(r"(예를들어|예컨대|가령|사례로|실제로)", t))

    if method == "인과":
        return bool(re.search(
            r"(때문에|이기때문에|따라서|그래서|그러므로|결과적으로|영향을)",
            t
        ))

    if method == "분석":
        return bool(re.search(
            r"(구성요소|부분|요소는|나누어|나누면|첫째|둘째|셋째)",
            t
        ))

    if method == "비교와 대조":
        return bool(re.search(
            r"(반면|반대로|차이|다르|같지만|공통점|차이점|비해|이라면)",
            t
        ))

    if method == "분류와 구분":
        return bool(re.search(
            r"(종류|유형|부류|나뉘|나누어|구분|분류|기준에따라)",
            t
        ))

    return False


def get_realized_methods(text):
    return [
        method for method in [
            "정의", "예시", "인과", "분석", "비교와 대조", "분류와 구분"
        ]
        if method_realized(text, method)
    ]


# ============================================================
# 문제 데이터
# ============================================================

QUESTIONS = {
    "1세트: 사회적 촉진·사회적 억제": {
        "1번": {
            "points": 3,
            "question": """다음 빈칸 ㉠~㉢에 들어갈 내용을 각각 쓰시오.

㉠ 사회적 촉진이 나타나기 쉬운 과제의 특징
㉡ 사회적 억제를 줄이기 위해 어려운 과제를 수행할 때의 방법
㉢ 어려운 과제를 다른 사람과 함께 수행할 때 나타나기 쉬운 현상""",
            "answer": [
                "㉠ 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제",
                "㉡ 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가짐",
                "㉢ 사회적 억제"
            ]
        },
        "2번": {
            "points": 4,
            "question": """다음 내용을 두 문장으로 설명하시오.

① 쉬운 과제와 어려운 과제를 수행할 때의 방법을 각각 설명할 것.
② (1)과 (2)에 각각 서로 다른 설명 방법을 1가지씩 활용할 것.
③ 설명 방법의 용어를 문장 끝에 괄호로 표시할 것.""",
            "answer": [
                "(1) 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제는 커피숍이나 도서관에서 하거나 다른 사람들과 함께 공부하는 것이 효율적이다. (분류)",
                "(2) 반면 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 혼자 차분하게 집중하는 것이 좋다. (대조)"
            ]
        },
        "3번": {
            "points": 4,
            "question": """어려운 과제를 수행할 때 사회적 억제를 줄이는 방법을 설명하는 영상을 제작하려 한다.

① 시각 요소 1가지를 제시할 것.
② 청각 요소 1가지를 제시할 것.
③ 각각의 요소가 시청자에게 어떤 효과를 주는지 설명할 것.""",
            "answer": [
                "시각: 조용한 방에서 한 학생이 어려운 문제를 혼자 해결하는 모습을 보여 준다.",
                "청각: 주변 소음을 줄이고 연필 소리나 종이 넘기는 소리를 작게 들려준다.",
                "효과: 혼자 차분하게 집중하는 상황을 효과적으로 전달한다."
            ]
        }
    },

    "2세트: 정전기": {
        "1번": {
            "points": 3,
            "question": """다음 빈칸 ㉠~㉢에 들어갈 내용을 각각 쓰시오.

㉠ 실생활에서 사용하는 전기가 ‘흐르는 물’이라면 정전기는 무엇에 해당하는가?
㉡ 정전기의 전하는 어떤 상태인가?
㉢ 정전기는 왜 위험하지 않은가?""",
            "answer": [
                "㉠ 높은 곳에 고여 있는 물",
                "㉡ 전하가 이동하지 않고 머물러 있음",
                "㉢ 전하가 이동하지 않고 머물러 있기 때문"
            ]
        },
        "2번": {
            "points": 4,
            "question": """다음 내용을 두 문장으로 설명하시오.

① 실생활의 전기와 정전기의 차이를 설명할 것.
② 정전기가 위험하지 않은 이유를 설명할 것.
③ (1)에는 한 가지 설명 방법을, (2)에는 (1)에서 사용하지 않은 다른 한 가지 설명 방법을 활용할 것.
④ 사용한 설명 방법을 문장 끝에 괄호로 표시할 것.""",
            "answer": [
                "(1) 실생활에서 쓰는 전기가 ‘흐르는 물’이라면, 정전기는 ‘높은 곳에 고여 있는 물’이라고 할 수 있다. (비교·대조)",
                "(2) 정전기는 전하가 이동하지 않고 머물러 있기 때문에 전압은 매우 높지만 위험하지 않다. (인과)"
            ]
        },
        "3번": {
            "points": 4,
            "question": """정전기의 특징을 설명하는 영상을 제작하려 한다.

① 정전기를 시각적으로 표현할 장면 1가지를 제시할 것.
② 정전기를 청각적으로 표현할 방법 1가지를 제시할 것.
③ 각각의 요소가 주는 효과를 설명할 것.""",
            "answer": [
                "시각: 높은 곳에 물이 고여 있고 흐르지 않는 장면을 보여 준다.",
                "청각: 흐르는 물 장면은 물소리를 크게 들려주고 정전기 장면은 조용하게 처리한다.",
                "효과: ‘흐르지 않고 머물러 있는 전기’라는 특징을 직관적으로 전달한다."
            ]
        }
    },

    "3세트: AI 생성 미술": {
        "1번": {
            "points": 5,
            "question": """다음 빈칸 ㉠~㉢에 들어갈 내용을 각각 쓰시오.

㉠ AI가 만든 그림과 관련된 대표적인 사례
㉡ AI 생성 미술을 예술로 보기 어렵다고 보는 근거
㉢ AI 생성 미술에도 가치가 있다고 보는 근거""",
            "answer": [
                "㉠ AI가 사람처럼 완벽하게 피겨 스케이팅을 수행하는 사례",
                "㉡ AI는 감정을 느끼지 못하고 독자적인 철학이나 이야기가 없어 예술로 보기 어렵다.",
                "㉢ 기존 미술계에 큰 변화를 가져오고 예술의 범주를 확장할 수 있어 상징적인 가치가 있다."
            ]
        },
        "2번": {
            "points": 4,
            "question": """다음 내용을 두 문장으로 설명하시오.

① 인간의 예술과 AI 생성 미술의 차이를 설명할 것.
② AI 생성 미술의 가치가 무엇인지 설명할 것.
③ (1)에는 한 가지 설명 방법을, (2)에는 (1)에서 사용하지 않은 다른 한 가지 설명 방법을 활용할 것.
④ 사용한 설명 방법을 문장 끝에 괄호로 표시할 것.""",
            "answer": [
                "(1) 인간의 예술에는 작가의 고유한 감정이나 철학, 삶의 경험 등이 담기지만 인공 지능은 감정을 느끼지 못하고 독자적인 철학이나 이야기가 없다. (대조)",
                "(2) 인공 지능이 그린 그림은 기존 미술계에 큰 변화를 가져왔기 때문에 앞으로 예술의 범주를 확장할 수 있다는 점에서 상징적인 가치가 있다. (인과)"
            ]
        },
        "3번": {
            "points": 6,
            "question": """AI 생성 미술의 특징을 소개하는 영상을 제작하려 한다.

① 인간 예술가의 작품 제작 모습을 시각 요소로 제시할 것.
② 인간 예술가의 감정이나 삶의 경험이 드러나는 청각 요소를 제시할 것.
③ 두 요소가 시청자에게 주는 효과를 설명할 것.""",
            "answer": [
                "시각: 인간 예술가가 자신의 경험과 생각을 떠올리며 작품을 만드는 모습을 보여 준다.",
                "청각: 예술가의 작품에 담긴 생각이나 경험을 인터뷰 또는 내레이션으로 들려준다.",
                "효과: 인간 예술에 작가의 감정과 삶의 경험이 담긴다는 점을 강조할 수 있다."
            ]
        }
    }
}


# ============================================================
# 채점 함수
# ============================================================

def grade_q1_set1(a):
    t = norm(a)
    checks = [
        any(x in t for x in ["쉬운", "큰노력을들일필요가없는", "노력이많이필요하지않"]),
        all(x in t for x in ["연습", "혼자"]) and any(x in t for x in ["익숙", "집중"]),
        "사회적억제" in t
    ]
    return sum(checks), checks


def grade_q2_set1(a):
    t = norm(a)
    easy = (
        any(x in t for x in ["쉬운", "취미"])
        and any(x in t for x in ["커피숍", "도서관", "다른사람", "함께"])
    )
    hard = (
        "어려운" in t
        and "연습" in t
        and "혼자" in t
        and any(x in t for x in ["익숙", "집중"])
    )

    realized = get_realized_methods(a)
    different = len(realized) >= 2

    score = int(easy) + int(hard) + (2 if different else 0)
    return score, [
        ("쉬운 과제의 수행 방법", easy),
        ("어려운 과제의 수행 방법", hard),
        ("서로 다른 설명 방법의 실제 구현", different)
    ]


def grade_q3_set1(a):
    t = norm(a)
    visual = any(x in t for x in ["혼자", "조용한방", "조용한곳", "어려운문제", "문제를푸는", "집중"])
    audio = any(x in t for x in ["주변소음", "소음을줄", "연필소리", "종이넘기는", "조용", "작게"])
    effect = any(x in t for x in ["집중", "차분", "사회적억제", "혼자"])
    return sum([visual, audio, effect]), [
        ("시각 요소", visual),
        ("청각 요소", audio),
        ("효과", effect)
    ]


def grade_q1_set2(a):
    t = norm(a)
    checks = [
        "높은곳" in t and "고여있는물" in t,
        "전하" in t and any(x in t for x in ["이동하지않", "머물"]),
        "전하" in t and any(x in t for x in ["이동하지않", "머물"]) and "위험하지않" in t
    ]
    return sum(checks), checks


def grade_q2_set2(a):
    t = norm(a)

    comparison = (
        ("흐르는물" in t and "고여있는물" in t)
        or ("전기" in t and "정전기" in t and
            any(x in t for x in ["흐르", "머물", "이동"]))
    )

    causality = (
        "전하" in t
        and any(x in t for x in ["이동하지않", "머물"])
        and any(x in t for x in ["때문", "따라서", "그래서"])
    )

    return int(comparison) + int(causality) + (
        2 if comparison and causality else 0
    ), [
        ("전기와 정전기의 차이", comparison),
        ("위험하지 않은 이유", causality),
        ("서로 다른 설명 방법", comparison and causality)
    ]


def grade_q3_set2(a):
    t = norm(a)
    visual = any(x in t for x in ["높은곳", "고여있는물", "흐르지", "멈춰", "정지"])
    audio = any(x in t for x in ["물소리", "흐르는소리", "조용", "소리를크게", "소리를작게", "소음"])
    effect = any(x in t for x in ["흐르지않", "머물", "정전기", "특징", "직관"])
    return sum([visual, audio, effect]), [
        ("시각 요소", visual),
        ("청각 요소", audio),
        ("효과", effect)
    ]


def grade_q1_set3(a):
    t = norm(a)
    checks = [
        any(x in t for x in ["로봇", "피겨"])
        and any(x in t for x in ["완벽", "실수없이"]),
        "ai" in t
        and any(x in t for x in ["감정", "철학", "이야기"])
        and any(x in t for x in ["없", "못"]),
        any(x in t for x in ["미술계", "예술"])
        and any(x in t for x in ["변화", "확장", "범주"])
    ]
    return sum(checks), checks


def grade_q2_set3(a):
    t = norm(a)

    contrast = (
        "인간" in t and "ai" in t
        and "감정" in t and "철학" in t
        and any(x in t for x in ["하지만", "반면", "없", "못"])
    )

    value = (
        "미술계" in t
        and any(x in t for x in ["변화", "확장", "범주"])
    )

    causal = any(x in t for x in ["때문", "따라서", "그래서"])
    different = contrast and causal

    return int(contrast) + int(value) + (2 if different else 0), [
        ("인간 예술과 AI의 차이", contrast),
        ("AI 생성 미술의 가치", value),
        ("서로 다른 설명 방법", different)
    ]


def grade_q3_set3(a):
    t = norm(a)
    visual = any(x in t for x in ["예술가", "작가", "작품을만", "그림을그", "작품제작"])
    audio = any(x in t for x in ["인터뷰", "내레이션", "말", "목소리", "경험", "생각"])
    effect = any(x in t for x in ["감정", "경험", "철학", "인간예술", "강조", "전달"])
    return sum([visual, audio, effect]), [
        ("시각 요소", visual),
        ("청각 요소", audio),
        ("효과", effect)
    ]


def grade_answer(set_name, q_name, answer):
    if set_name.startswith("1세트") and q_name == "1번":
        return grade_q1_set1(answer)
    if set_name.startswith("1세트") and q_name == "2번":
        return grade_q2_set1(answer)
    if set_name.startswith("1세트") and q_name == "3번":
        return grade_q3_set1(answer)

    if set_name.startswith("2세트") and q_name == "1번":
        return grade_q1_set2(answer)
    if set_name.startswith("2세트") and q_name == "2번":
        return grade_q2_set2(answer)
    if set_name.startswith("2세트") and q_name == "3번":
        return grade_q3_set2(answer)

    if set_name.startswith("3세트") and q_name == "1번":
        return grade_q1_set3(answer)
    if set_name.startswith("3세트") and q_name == "2번":
        return grade_q2_set3(answer)
    if set_name.startswith("3세트") and q_name == "3번":
        return grade_q3_set3(answer)

    return 0, []


# ============================================================
# Streamlit 화면
# ============================================================

st.title("📝 서논술형 자동 채점")

st.info(
    "문제와 조건을 먼저 확인한 뒤 답안을 작성하세요. "
    "설명 방법은 용어만 적는 것이 아니라 실제 특성이 드러나는지도 확인합니다."
)

set_name = st.selectbox("문제 세트", list(QUESTIONS.keys()))
q_name = st.selectbox("문항", list(QUESTIONS[set_name].keys()))
q = QUESTIONS[set_name][q_name]

st.divider()

# 문제를 답안보다 먼저 크게 표시
st.subheader(f"📖 {q_name} 문제")

st.markdown(
    f"""
    <div style="
        background-color: #f7f7f7;
        border: 1px solid #d9d9d9;
        border-radius: 12px;
        padding: 24px;
        font-size: 17px;
        line-height: 1.9;
        white-space: pre-wrap;
    ">{q["question"]}</div>
    """,
    unsafe_allow_html=True
)

st.subheader("💡 모범 답안")

with st.expander("모범 답안 펼쳐 보기", expanded=False):
    for item in q["answer"]:
        st.markdown(f"- {item}")

st.divider()

st.subheader("✍️ 답안 작성")

placeholder = (
    "㉠~㉢의 답을 작성하세요."
    if q_name == "1번"
    else "(1), (2)를 구분하여 작성하세요."
    if q_name == "2번"
    else "시각 요소, 청각 요소, 효과를 포함하여 작성하세요."
)

answer = st.text_area(
    "학생 답안",
    height=240,
    placeholder=placeholder,
    key=f"answer_{set_name}_{q_name}"
)

if st.button("🔎 자동 채점", type="primary", use_container_width=True):
    if not answer.strip():
        st.warning("답안을 먼저 작성해 주세요.")
    else:
        score, details = grade_answer(set_name, q_name, answer)
        max_score = q["points"]
        score = min(score, max_score)

        st.divider()
        st.subheader("📊 채점 결과")

        if score == max_score:
            st.success(f"**{score} / {max_score}점** — 조건을 충족했습니다.")
        elif score >= max_score / 2:
            st.warning(f"**{score} / {max_score}점** — 일부 조건을 충족했습니다.")
        else:
            st.error(f"**{score} / {max_score}점** — 핵심 조건을 다시 확인하세요.")

        st.markdown("### 세부 판정")

        for detail in details:
            if isinstance(detail, tuple):
                label, ok = detail
                st.write(("✅ " if ok else "❌ ") + label)
            else:
                st.write(("✅ " if detail else "❌ ") + "조건")

        if q_name == "2번":
            st.markdown("### 설명 방법 확인")

            realized = get_realized_methods(answer)
            labels = detect_method_label(answer)

            if realized:
                st.write(
                    "실제로 드러난 설명 방법: "
                    + ", ".join(realized)
                )
            else:
                st.write("실제로 드러난 설명 방법을 찾지 못했습니다.")

            if labels:
                st.write(
                    "답안에 적힌 방법 용어: "
                    + ", ".join(labels)
                )

            if labels and not realized:
                st.warning(
                    "설명 방법의 용어만 적고 실제 특성이 드러나지 않은 경우에는 "
                    "해당 방법을 인정하지 않습니다."
                )

st.divider()

st.subheader("📌 자동 채점 원칙")

st.markdown("""
- **용어 없이도 인정:** 설명 방법의 의미와 실제 구조가 답안에 드러나면 인정합니다.
- **방법의 특성 확인:** `(대조)`, `(인과)` 등의 용어만 적은 경우에는 실제 내용이 해당 방법을 구현해야 합니다.
- **오개념 방지:** 다른 개념의 특성을 잘못 가져와 설명한 경우 해당 조건을 충족한 것으로 보지 않습니다.
- **결론 방향 확인:** 문제에서 요구한 방향의 결론이 답안에 명확하게 드러나야 통과합니다.
- **현재 9개 문항에는 객관식 선택지가 없습니다.**
""")

st.caption(
    "※ 규칙 기반 자동 채점 결과이므로 최종 성적 산정 전 교사의 확인을 권장합니다."
)
