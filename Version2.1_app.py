import streamlit as st
import pandas as pd

# ==================================================
# ページ設定
# ==================================================

st.set_page_config(
    page_title="ジャグラー実戦アシスタント",
    layout="wide"
)

# ==================================================
# 関数
# ==================================================

def calc_realtime_score(game, bb, rb):

    if game < 500:
        return 20

    if rb <= 0:
        return 10

    rb_rate = game / rb

    if rb_rate <= 230:
        score = 100

    elif rb_rate <= 260:
        score = 90

    elif rb_rate <= 290:
        score = 80

    elif rb_rate <= 330:
        score = 65

    elif rb_rate <= 370:
        score = 50

    else:
        score = 25

    confidence = min(game / 5000, 1.0)

    return round(score * confidence, 1)


def calc_recent_score(
    start_g,
    start_bb,
    start_rb,
    now_g,
    now_bb,
    now_rb
):

    diff_g = now_g - start_g
    diff_rb = now_rb - start_rb

    if diff_g <= 0:
        return 0

    if diff_rb <= 0:
        return 10

    recent_rb_rate = diff_g / diff_rb

    if recent_rb_rate <= 180:
        return 100

    elif recent_rb_rate <= 220:
        return 90

    elif recent_rb_rate <= 260:
        return 75

    elif recent_rb_rate <= 320:
        return 60

    elif recent_rb_rate <= 400:
        return 40

    return 20


def calc_sign_bonus(sign_text):

    bonus = 0

    if pd.isna(sign_text):
        return 0

    sign_text = str(sign_text)

    if "急凹み" in sign_text:
        bonus += 3

    if "大凹み" in sign_text:
        bonus += 2

    if "末尾狙い" in sign_text:
        bonus += 3

    if "角候補" in sign_text:
        bonus += 2

    return bonus


def judge(score):

    if score >= 90:
        return "★★★★★ 超本命"

    elif score >= 80:
        return "★★★★☆ 激アツ"

    elif score >= 70:
        return "★★★☆☆ 続行推奨"

    elif score >= 60:
        return "★★☆☆☆ 様子見"

    return "★☆☆☆☆ ヤメ候補"


# ==================================================
# タイトル
# ==================================================

st.title("ジャグラー実戦アシスタント V2.1")

store = st.radio(
    "店舗選択",
    [
        "ニラク",
        "マルハン"
    ]
)

uploaded_file = st.file_uploader(
    "予測ファイル(xlsx)",
    type=["xlsx"]
)

if uploaded_file is None:
    st.stop()

# ==================================================
# ニラク
# ==================================================

if store == "ニラク":

    ai_df = pd.read_excel(
        uploaded_file,
        sheet_name="AI＋人間"
    )

    human_df = pd.read_excel(
        uploaded_file,
        sheet_name="人間予想ランキング"
    )

    machine_list = sorted(
        ai_df["台番号"].unique()
    )

    target_machine = st.selectbox(
        "台番号",
        machine_list
    )

    ai_row = ai_df[
        ai_df["台番号"] == target_machine
    ].iloc[0]

    human_row = human_df[
        human_df["台番号"] == target_machine
    ].iloc[0]

    base_score = float(
        ai_row["AI人間総合"]
    )

    sign_bonus = calc_sign_bonus(
        human_row["狙いサイン"]
    )

# ==================================================
# マルハン
# ==================================================

else:

    rank_df = pd.read_excel(
        uploaded_file,
        sheet_name="ランキング"
    )

    machine_list = sorted(
        rank_df["台番号"].unique()
    )

    target_machine = st.selectbox(
        "台番号",
        machine_list
    )

    row = rank_df[
        rank_df["台番号"] == target_machine
    ].iloc[0]

    base_score = float(
        row["高設定期待度"]
    )

    sign_bonus = 0

# ==================================================
# 開始データ
# ==================================================

st.subheader("打ち始めデータ")

c1, c2, c3 = st.columns(3)

with c1:

    start_g = st.number_input(
        "開始G数",
        0,
        20000,
        3000
    )

with c2:

    start_bb = st.number_input(
        "開始BB",
        0,
        100,
        10
    )

with c3:

    start_rb = st.number_input(
        "開始RB",
        0,
        100,
        10
    )

# ==================================================
# 現在データ
# ==================================================

st.subheader("現在データ")

c1, c2, c3 = st.columns(3)

with c1:

    now_g = st.number_input(
        "現在G数",
        0,
        30000,
        3500
    )

with c2:

    now_bb = st.number_input(
        "現在BB",
        0,
        150,
        15
    )

with c3:

    now_rb = st.number_input(
        "現在RB",
        0,
        150,
        13
    )

# ==================================================
# 判定
# ==================================================

if st.button("判定開始"):

    realtime_score = calc_realtime_score(
        now_g,
        now_bb,
        now_rb
    )

    recent_score = calc_recent_score(
        start_g,
        start_bb,
        start_rb,
        now_g,
        now_bb,
        now_rb
    )

    final_score = (
        base_score * 0.5
        + realtime_score * 0.3
        + recent_score * 0.2
        + sign_bonus
    )

    final_score = min(
        round(final_score, 1),
        100
    )

    # =======================================

    st.header(
        f"総合期待度 : {final_score}点"
    )

    st.success(
        judge(final_score)
    )

    st.progress(
        int(final_score)
    )

    # =======================================
    # メトリクス
    # =======================================

    a, b, c, d = st.columns(4)

    with a:
        st.metric(
            "朝評価",
            round(base_score, 1)
        )

    with b:
        st.metric(
            "実戦評価",
            round(realtime_score, 1)
        )

    with c:
        st.metric(
            "直近評価",
            round(recent_score, 1)
        )

    with d:
        st.metric(
            "サイン補正",
            sign_bonus
        )

    # =======================================
    # 現在確率
    # =======================================

    st.subheader("現在スペック")

    col1, col2, col3 = st.columns(3)

    if now_rb > 0:

        with col1:
            st.metric(
                "REG",
                f"1/{now_g/now_rb:.1f}"
            )

    if now_bb > 0:

        with col2:
            st.metric(
                "BIG",
                f"1/{now_g/now_bb:.1f}"
            )

    if now_bb + now_rb > 0:

        with col3:
            st.metric(
                "合算",
                f"1/{now_g/(now_bb+now_rb):.1f}"
            )

    # =======================================
    # 直近挙動
    # =======================================

    diff_g = now_g - start_g
    diff_bb = now_bb - start_bb
    diff_rb = now_rb - start_rb

    st.subheader("直近挙動")

    st.write(
        f"追加G数 : {diff_g}"
    )

    st.write(
        f"追加BB : +{diff_bb}"
    )

    st.write(
        f"追加RB : +{diff_rb}"
    )

    if diff_rb > 0:

        recent_rb = diff_g / diff_rb

        st.metric(
            "直近REG",
            f"1/{recent_rb:.1f}"
        )

    # =======================================
    # ニラク追加表示
    # =======================================

    if store == "ニラク":

        st.subheader("朝予測情報")

        st.write(
            f"AI人間順位 : {int(ai_row['AI人間順位'])}"
        )

        st.write(
            f"AI人間総合 : {ai_row['AI人間総合']:.1f}"
        )

        st.write(
            f"AIスコア : {ai_row['AIスコア']:.1f}"
        )

        st.write(
            f"人間予想スコア : {human_row['人間予想スコア']:.1f}"
        )

        st.write(
            f"人間ランク : {human_row['人間ランク']}"
        )

        st.write(
            f"位置区分 : {human_row['位置区分']}"
        )

        st.write(
            f"凹み加速 : {human_row['凹み加速']:.0f}"
        )

        st.write(
            f"狙いサイン : {human_row['狙いサイン']}"
        )

    else:

        st.subheader("朝予測情報")

        st.write(
            f"順位 : {row['順位']}"
        )

        st.write(
            f"高設定期待度 : {row['高設定期待度']:.1f}"
        )

        st.write(
            f"機種 : {row['機種名']}"
        )

        st.write(
            f"末尾 : {row['末尾']}"
        )