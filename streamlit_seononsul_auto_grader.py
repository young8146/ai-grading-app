
import re
import streamlit as st

st.set_page_config(page_title="서논술형 자동 채점", page_icon="📝", layout="wide")

# ============================================================
# 1. 공통 텍스트 처리
# ============================================================
def norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[“”‘’\"'.,!?;:()\[\]{}<>·\-_/]", "", s)
    return s

def has_any(text, patterns):
    t = norm(text)
    return any(norm(p) in t for p in patterns)

def has_all(text, patterns):
    t = norm(text)
    return all(norm(p) in t for p in patterns)

def score_item(ok, max_score, reason):
    return {"score": max_score if ok else 0, "max": max_score, "ok": ok, "reason": reason}

# ============================================================
# 2. 설명 방법 판별
#    핵심: 용어가 없어도 '방법의 구조/의미'가 있으면 인정.
# ============================================================
METHOD_PATTERNS = {
    "정의": [
        r"이란", r"말한다", r"뜻이다", r"뜻을말한다", r"라고한다",
        r"의미한다", r"~이다"
    ],
    "예시": [
        r"예를들어", r"예컨대", r"대표적으로", r"예로는", r"사례"
    ],
    "인과": [
        r"때문에", r"기때문에", r"어서", r"아서", r"므로", r"따라서",
        r"그결과", r"원인", r"결과", r"영향을주", r"~기때문"
    ],
    "분석": [
        r"부분", r"요소", r"구성", r"이루어져", r"나뉘어",
        r"머리", r"몸통", r"팔", r"다리"
    ],
    "비교와 대조": [
        r"반면", r"다르", r"공통점", r"차이점", r"비교", r"비해",
        r"같지만", r"와는달리", r"반대로"
    ],
    "분류와 구분": [
        r"종류", r"묶", r"나누", r"분류", r"구분", r"~에따라",
        r"에따라"
    ],
}

def detect_method(text):
    t = norm(text)
    found = []
    for method, pats in METHOD_PATTERNS.items():
        if any(norm(p).replace("\\","") in t for p in pats):
            found.append(method)
    return found

# 보다 엄격한 의미 기반 판정.
# 학생이 방법 명칭을 쓰지 않았더라도 아래의 '구조'가 나타나면 인정한다.
def method_realized(text, method):
    t = norm(text)
    if method == "정의":
        return has_any(t, ["이란", "말한다", "뜻이다", "라고한다", "의미한다"])
    if method == "예시":
        return has_any(t, ["예를들어", "예컨대", "대표적으로", "예로는"])
    if method == "인과":
        # 원인/결과 관계가 명확한 경우만 인정
        return (
            has_any(t, ["때문에", "기때문에", "어서", "아서", "므로", "따라서", "그결과"])
            and
            has_any(t, ["그래서", "따라서", "결과", "효율", "위험", "가치", "변화", "예술"])
        )
    if method == "분석":
        return (
            has_any(t, ["구성", "이루어져", "부분", "요소"])
            and has_any(t, ["머리", "가슴", "배", "요소", "부분", "종류"])
        )
    if method == "비교와 대조":
        return has_any(t, ["반면", "다르", "공통점", "차이점", "비해", "같지만", "와는달리"])
    if method == "분류와 구분":
        return (
            has_any(t, ["종류", "묶", "나누", "분류", "구분"])
            and has_any(t, ["기준", "에따라", "으로나뉘", "로묶"])
        )
    return False

# ============================================================
# 3. 세트 1
# ============================================================
def grade_s1_q1(a1, a2, a3):
    r = {}
    r["㉠"] = score_item(
        has_any(a1, ["비교적쉬운", "쉬운", "큰노력을들일필요가없는", "노력이많이필요하지않은"])
        and has_any(a1, ["과제", "취미"]),
        1, "쉬운/노력이 적은 과제라는 특성이 필요합니다."
    )
    r["㉡"] = score_item(
        has_any(a2, ["충분히연습", "연습"])
        and has_any(a2, ["익숙", "익숙해질"])
        and has_any(a2, ["혼자"])
        and has_any(a2, ["차분", "집중"]),
        1, "충분한 연습·익숙해짐과 혼자 차분히 집중한다는 내용이 필요합니다."
    )
    r["㉢"] = score_item(
        has_any(a3, ["사회적억제"]),
        1, "심리 현상명 '사회적 억제'가 필요합니다."
    )
    return r

def grade_s1_q2(a1, a2):
    # 내용 + 서로 다른 설명 방법 + 실제 방법 특성
    content1 = has_any(a1, ["쉬운", "비교적쉬운", "큰노력을들일필요가없는"]) and has_any(a1, ["커피숍", "도서관", "다른사람", "함께", "모임"])
    content2 = has_any(a2, ["어렵", "복잡", "도전"]) and has_any(a2, ["충분히연습", "익숙"]) and has_any(a2, ["혼자", "차분", "집중"])
    m1 = detect_method(a1)
    m2 = detect_method(a2)
    realized = [(m, method_realized(a1, m)) for m in m1] + [(m, method_realized(a2, m)) for m in m2]
    method_ok1 = any(ok for m, ok in realized)
    method_ok2 = any(ok for m, ok in [(m, method_realized(a2, m)) for m in m2])
    different = bool(set(m1) & set(m2) == set()) and method_ok1 and method_ok2
    # 용어만 쓰고 구조가 없는 경우는 불인정
    ok = content1 and content2 and different
    reason = f"(1) 내용={content1}, (2) 내용={content2}, 설명 방법 실제 구현={different}"
    return score_item(ok, 4, reason)

def grade_s1_q3(a, b):
    visual = has_any(a, ["혼자", "한명", "학생"]) and has_any(a, ["어려운", "어렵", "복잡", "도전"]) and has_any(a, ["조용", "차분", "집중"])
    audio = has_any(b, ["조용", "소리없", "배경음악없", "작은소리", "연필", "페이지"]) and not has_any(b, ["시끄럽", "경쾌", "리듬감"])
    effect_a = has_any(a, ["효과", "전달", "집중", "차분", "혼자"])
    effect_b = has_any(b, ["효과", "전달", "집중", "차분", "소음"])
    return {
        "Ⓐ": score_item(visual and effect_a, 2, "어려운 과제에 맞는 혼자·차분·집중 환경과 그 효과가 필요합니다."),
        "Ⓑ": score_item(audio and effect_b, 2, "조용한 청각 환경과 그 효과가 필요합니다.")
    }

# ============================================================
# 4. 세트 2
# ============================================================
def grade_s2_q1(a1, a2, a3):
    return {
        "㉠": score_item(has_any(a1, ["높은곳에고여있는물", "고여있는물", "높은곳에고인물"]), 1,
                        "높은 곳에 고여 있는 물이 핵심입니다."),
        "㉡": score_item(has_any(a2, ["전하가이동하지않", "전하가머물", "이동하지않고머물"]), 1,
                        "전하가 이동하지 않고 머물러 있다는 내용이 필요합니다."),
        "㉢": score_item(has_any(a3, ["위험하지않", "위험하지않다", "감전위험이없", "피해가없"]), 1,
                        "전하가 이동하지 않아 위험하지 않다는 결론 방향이어야 합니다.")
    }

def grade_s2_q2(a1, a2):
    # 가능한 안정적 조합: 비교·대조 / 인과, 정의 / 인과
    s1_content = has_any(a1, ["실생활전기", "평소사용하는전기", "흐르는물"]) or has_any(a1, ["정전기"])
    s2_content = has_any(a2, ["전하가이동하지않", "전하가머물"]) and has_any(a2, ["전압", "위험하지않", "위험"])
    methods1 = [m for m in METHOD_PATTERNS if method_realized(a1, m)]
    methods2 = [m for m in METHOD_PATTERNS if method_realized(a2, m)]
    # 핵심 오개념 차단
    wrong = has_any(a1+a2, ["정전기는전하가이동", "정전기는흐르는전기", "정전기는위험하다"])
    different = bool(set(methods1).isdisjoint(set(methods2)))
    ok = s1_content and s2_content and bool(methods1) and bool(methods2) and different and not wrong
    return score_item(ok, 4, f"방법={methods1}/{methods2}, 내용 충족={s1_content and s2_content}, 오개념={wrong}")

def grade_s2_q3(a, b):
    visual = has_any(a, ["고여있는물", "높은곳", "정지", "가만히", "움직이지않"]) and has_any(a, ["전하", "정전기", "머물"])
    audio = has_any(b, ["조용", "작은소리", "잔잔", "물방울", "고요", "소리없"]) and not has_any(b, ["웅장", "거센", "큰소리", "콸콸"])
    effect_a = has_any(a, ["효과", "전달", "전하", "머물", "움직이지"])
    effect_b = has_any(b, ["효과", "전달", "조용", "차분", "고여"])
    return {
        "Ⓐ": score_item(visual and effect_a, 2, "고여 있고 움직이지 않는 정전기의 특성이 시각적으로 드러나야 합니다."),
        "Ⓑ": score_item(audio and effect_b, 2, "장면1의 큰 소리와 대비되는 조용한 청각 요소 및 효과가 필요합니다.")
    }

# ============================================================
# 5. 세트 3
# ============================================================
def grade_s3_q1(a1, a2, a3):
    return {
        "㉠": score_item(has_any(a1, ["로봇", "인공지능", "ai"]) and has_any(a1, ["피겨", "스케이팅", "완벽", "실수없이"]), 1,
                        "로봇이 실수 없이 완벽하게 피겨 스케이팅을 하는 예가 필요합니다."),
        "㉡": score_item(
            has_any(a2, ["예술로보기어렵", "예술로볼수없", "예술이라보기어렵"])
            and has_any(a2, ["감정", "철학", "이야기"]),
            2, "AI를 예술로 보기 어렵다는 결론과 감정·독자적 철학·이야기 부재의 근거가 필요합니다."
        ),
        "㉢": score_item(
            has_any(a3, ["기존미술계", "미술계"]) and has_any(a3, ["변화", "큰변화"])
            and has_any(a3, ["예술의범주", "범주", "확장"]),
            2, "미술계의 변화와 예술 범주 확장이라는 두 가치가 필요합니다."
        )
    }

def grade_s3_q2(a1, a2):
    human = has_any(a1, ["인간의예술", "인간의작품", "작가"]) and has_any(a1, ["감정", "철학", "삶의경험", "관점", "환경"])
    ai_lack = has_any(a1+a2, ["ai", "인공지능"]) and has_any(a1+a2, ["감정이없", "감정을느끼지못", "독자적인철학이없", "철학이나이야기가없"])
    value = has_any(a2, ["기존미술계", "미술계"]) and has_any(a2, ["변화"]) and has_any(a2, ["범주", "확장", "상징적인가치"])
    m1 = [m for m in METHOD_PATTERNS if method_realized(a1, m)]
    m2 = [m for m in METHOD_PATTERNS if method_realized(a2, m)]
    wrong = has_any(a1+a2, ["ai는감정이있", "ai의독자적인철학이있", "ai는인간과같은감정이있"])
    different = bool(set(m1).isdisjoint(set(m2)))
    ok = human and ai_lack and value and bool(m1) and bool(m2) and different and not wrong
    return score_item(ok, 4, f"인간/AI 대조={human and ai_lack}, AI 가치={value}, 방법={m1}/{m2}, 오개념={wrong}")

# ============================================================
# 6. 세트 3 Q3
# ============================================================
def grade_s3_q3(a, b):
    visual = has_any(a, ["작가", "사람", "인간"]) and has_any(a, ["그림", "작품", "만들", "그리"]) and has_any(a, ["감정", "경험", "철학", "관점"])
    audio = has_any(b, ["작가의목소리", "작가가말", "인터뷰", "이야기", "음성", "내레이션", "생각", "경험"]) and has_any(b, ["감정", "경험", "철학", "관점", "마음"])
    effect_a = has_any(a, ["효과", "전달", "감정", "경험", "철학", "관점"])
    effect_b = has_any(b, ["효과", "전달", "감정", "경험", "철학", "마음", "울림"])
    return {
        "Ⓐ": score_item(visual and effect_a, 3, "인간 작가의 작업과 감정·경험·철학·관점이 드러나는 시각 연출 및 근거가 필요합니다."),
        "Ⓑ": score_item(audio and effect_b, 3, "작가의 경험·생각 등을 전달하는 청각 연출 및 근거가 필요합니다.")
    }

# ============================================================
# 7. UI
# ============================================================
st.title("📝 서논술형 자동 채점 웹앱")
st.caption("키워드 단순 일치가 아니라 '내용 + 결론 방향 + 설명 방법의 실제 구현 + 오개념'을 함께 검사합니다.")

set_name = st.sidebar.selectbox("세트", ["1세트", "2세트", "3세트"])
q_name = st.sidebar.selectbox("문항", ["1번", "2번", "3번"])

st.info("현재 버전은 규칙 기반 자동 채점입니다. 문장 표현이 매우 다양한 경우 교사 검토용 '판정 근거'를 함께 표시합니다.")

if set_name == "1세트" and q_name == "1번":
    st.subheader("1세트 1번")
    a1 = st.text_input("㉠")
    a2 = st.text_input("㉡")
    a3 = st.text_input("㉢")
    if st.button("채점"):
        r = grade_s1_q1(a1,a2,a3)
        total = sum(x["score"] for x in r.values())
        st.success(f"점수: {total}/3")
        for k,v in r.items(): st.write(f"**{k}**: {v['score']}/{v['max']} — {v['reason']}")

elif set_name == "1세트" and q_name == "2번":
    st.subheader("1세트 2번")
    a1 = st.text_area("(1)")
    a2 = st.text_area("(2)")
    if st.button("채점"):
        r = grade_s1_q2(a1,a2)
        st.success(f"점수: {r['score']}/{r['max']}")
        st.write(r["reason"])

elif set_name == "1세트" and q_name == "3번":
    st.subheader("1세트 3번")
    a = st.text_area("시각 요소 Ⓐ + 효과")
    b = st.text_area("청각 요소 Ⓑ + 효과")
    if st.button("채점"):
        r = grade_s1_q3(a,b)
        st.success(f"점수: {sum(x['score'] for x in r.values())}/4")
        for k,v in r.items(): st.write(f"**{k}**: {v['score']}/{v['max']} — {v['reason']}")

elif set_name == "2세트" and q_name == "1번":
    st.subheader("2세트 1번")
    a1 = st.text_input("㉠")
    a2 = st.text_input("㉡")
    a3 = st.text_input("㉢")
    if st.button("채점"):
        r = grade_s2_q1(a1,a2,a3)
        st.success(f"점수: {sum(x['score'] for x in r.values())}/3")
        for k,v in r.items(): st.write(f"**{k}**: {v['score']}/{v['max']} — {v['reason']}")

elif set_name == "2세트" and q_name == "2번":
    st.subheader("2세트 2번")
    a1 = st.text_area("(1)")
    a2 = st.text_area("(2)")
    if st.button("채점"):
        r = grade_s2_q2(a1,a2)
        st.success(f"점수: {r['score']}/{r['max']}")
        st.write(r["reason"])

elif set_name == "2세트" and q_name == "3번":
    st.subheader("2세트 3번")
    a = st.text_area("시각 요소 Ⓐ + 효과")
    b = st.text_area("청각 요소 Ⓑ + 효과")
    if st.button("채점"):
        r = grade_s2_q3(a,b)
        st.success(f"점수: {sum(x['score'] for x in r.values())}/4")
        for k,v in r.items(): st.write(f"**{k}**: {v['score']}/{v['max']} — {v['reason']}")

elif set_name == "3세트" and q_name == "1번":
    st.subheader("3세트 1번")
    a1 = st.text_input("㉠")
    a2 = st.text_input("㉡")
    a3 = st.text_input("㉢")
    if st.button("채점"):
        r = grade_s3_q1(a1,a2,a3)
        st.success(f"점수: {sum(x['score'] for x in r.values())}/5")
        for k,v in r.items(): st.write(f"**{k}**: {v['score']}/{v['max']} — {v['reason']}")

elif set_name == "3세트" and q_name == "2번":
    st.subheader("3세트 2번")
    a1 = st.text_area("(1)")
    a2 = st.text_area("(2)")
    if st.button("채점"):
        r = grade_s3_q2(a1,a2)
        st.success(f"점수: {r['score']}/{r['max']}")
        st.write(r["reason"])

elif set_name == "3세트" and q_name == "3번":
    st.subheader("3세트 3번")
    a = st.text_area("시각 요소 Ⓐ + 효과")
    b = st.text_area("청각 요소 Ⓑ + 효과")
    if st.button("채점"):
        r = grade_s3_q3(a,b)
        st.success(f"점수: {sum(x['score'] for x in r.values())}/6")
        for k,v in r.items(): st.write(f"**{k}**: {v['score']}/{v['max']} — {v['reason']}")

st.divider()
st.markdown("### 선택지별 모범 답안")
st.write("현재 9문항은 실제 객관식 선택지가 없으므로 선택지별 모범 답안은 '해당 없음'입니다.")
st.markdown("""
**1세트 1번**: ㉠ 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제 / ㉡ 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가짐 / ㉢ 사회적 억제

**1세트 2번**: (1) 쉬운 과제는 커피숍·도서관 또는 다른 사람들과 함께 하는 것이 효율적임(분류/구분 구조를 실제로 보여야 함), (2) 어려운 과제는 충분히 연습하고 익숙해질 때까지 혼자 차분하게 집중하는 것이 좋음(대조 등).

**1세트 3번**: Ⓐ 어려운 과제를 혼자 차분하게 집중하는 학생을 조용한 공간에서 보여줌 / Ⓑ 배경음악을 줄이고 연필·페이지 넘기는 작은 소리 등을 사용함.

**2세트 1번**: ㉠ 높은 곳에 고여 있는 물 / ㉡ 전하가 이동하지 않고 머물러 있음 / ㉢ 위험하지 않음.

**2세트 2번**: (1) 실생활 전기가 흐르는 물이라면 정전기는 높은 곳에 고여 있는 물이라고 할 수 있음(비교·대조), (2) 정전기는 전하가 이동하지 않고 머물러 있기 때문에 전압은 매우 높지만 위험하지 않음(인과).

**2세트 3번**: Ⓐ 고여 있는 물처럼 움직이지 않는 모습을 보여 줌 / Ⓑ 잔잔하고 작은 소리 또는 거의 소리가 없는 연출을 사용함.

**3세트 1번**: ㉠ 로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 함 / ㉡ AI는 감정을 느끼지 못하고 독자적인 철학이나 이야기가 없어 예술로 보기 어려움 / ㉢ 기존 미술계에 큰 변화를 가져오며 예술의 범주를 확장할 수 있다는 상징적 가치가 있음.

**3세트 2번**: (1) 인간의 예술에는 작가의 고유한 감정·철학·삶의 경험 등이 담기지만 AI는 감정을 느끼지 못하고 독자적인 철학이나 이야기가 없음(대조), (2) AI 그림은 기존 미술계에 큰 변화를 가져왔고 예술의 범주를 확장할 수 있다는 상징적 가치가 있음(인과).

**3세트 3번**: Ⓐ 작가가 자신의 경험과 생각을 떠올리며 작품을 만드는 모습을 보여 줌 / Ⓑ 작가의 경험이나 작품에 담긴 생각을 말하는 내레이션·인터뷰를 넣음.
""")
