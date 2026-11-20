import streamlit as st

from modules.i18n import get_ui_language, tr
from modules.research_data import (
    ACOUSTIC_PAPER_CITATION,
    ACOUSTIC_PAPER_DOI,
    PAPER_CITATION,
    PAPER_DOI,
    build_c_index_figure,
)
from modules.ui import render_brand


_USER_COPY = {
    "zh-Hant": {
        "title": "研究結果，用生活話來說",
        "slogan": "多一份熟悉的觀察，讓生活變化更容易被看見。",
        "story": (
            "研究團隊先看常見健康資料，再看看「有沒有取得熟悉者填寫的問卷」，"
            "最後再加入問卷分數。三種資料組合的研究表現依序提高。"
        ),
        "scale": "簡化成 0 到 100 分，方便看出三種資料組合的差異。",
        "step_base": "常見資料｜約 68 分",
        "step_availability": "問卷資料是否齊全｜約 73 分",
        "step_ecog": "再加入問卷分數｜約 76 分",
        "caveat": "分數只用來比較三種資料組合的研究表現。",
        "analogy_title": "多一份觀察，像多一個生活視角",
        "analogy": (
            "就像本人分享日常，再由熟悉你的人補上一份問卷，研究團隊便多一個角度。"
            "這項研究比較的是問卷資料是否取得。"
        ),
        "academic_toggle": "🔬 給評審／研究者看｜研究依據（點擊展開）",
        "academic_heading": "研究依據",
        "academic_values": (
            "**M2：0.680 → 加入配對資料可得性：0.733 → M3：0.758**\n\n"
            "配對資料可得性增量：ΔC = 0.052（95% CI：0.023–0.082）  \n"
            "再加入 ECog 分數的增量：ΔC = 0.026（95% CI：0.007–0.045）"
        ),
        "acoustic_heading": "聲學指標依據",
        "acoustic_note": (
            "本產品語音面板計算的停頓比例、停頓時長與音調變異度（F0 標準差），"
            "沿用下列奠基性研究驗證的語音數位表型：敘事語音中的聲學與語言特徵"
            "可區分阿茲海默症患者，其中停頓與語速特徵是重要預測因子。"
        ),
    },
    "zh-Hans": {
        "title": "研究结果，用生活话来说",
        "slogan": "多一份熟悉的观察，让生活变化更容易被看见。",
        "story": (
            "研究团队先看常见健康资料，再看看“是否取得熟悉者填写的问卷”，"
            "最后再加入问卷分数。三种资料组合的研究表现依次提高。"
        ),
        "scale": "简化成 0 到 100 分，方便看出三种资料组合的差异。",
        "step_base": "常见资料｜约 68 分",
        "step_availability": "问卷资料是否齐全｜约 73 分",
        "step_ecog": "再加入问卷分数｜约 76 分",
        "caveat": "分数只用来比较三种资料组合的研究表现。",
        "analogy_title": "多一份观察，像多一个生活视角",
        "analogy": (
            "就像本人分享日常，再由熟悉你的人补上一份问卷，研究团队便多一个角度。"
            "这项研究比较的是问卷资料是否取得。"
        ),
        "academic_toggle": "🔬 给评委／研究者看｜研究依据（点击展开）",
        "academic_heading": "研究依据",
        "academic_values": (
            "**M2：0.680 → 加入配对资料可得性：0.733 → M3：0.758**\n\n"
            "配对资料可得性增量：ΔC = 0.052（95% CI：0.023–0.082）  \n"
            "再加入 ECog 分数的增量：ΔC = 0.026（95% CI：0.007–0.045）"
        ),
        "acoustic_heading": "声学指标依据",
        "acoustic_note": (
            "本产品语音面板计算的停顿比例、停顿时长与音调变异度（F0 标准差），"
            "沿用下列奠基性研究验证的语音数字表型：叙事语音中的声学与语言特征"
            "可区分阿尔茨海默症患者，其中停顿与语速特征是重要预测因子。"
        ),
    },
    "en": {
        "title": "The research, in everyday language",
        "slogan": "A familiar perspective can help make everyday changes easier to see.",
        "story": (
            "Researchers first used common health information, then checked whether a "
            "paired questionnaire from someone familiar was available, and finally added "
            "the questionnaire scores. The group-level model results increased at each step."
        ),
        "scale": "Shown on a simple 0–100 scale to make the difference between the three data setups easy to see.",
        "step_base": "Common information · about 68",
        "step_availability": "Paired questionnaire available · about 73",
        "step_ecog": "Questionnaire scores added · about 76",
        "caveat": "The scores only compare the three data setups in the study.",
        "analogy_title": "Another questionnaire adds another view of daily life",
        "analogy": (
            "Like hearing someone's own account and also having a questionnaire from someone "
            "who knows them, researchers get another perspective. The study compared whether "
            "paired data were available."
        ),
        "academic_toggle": "🔬 For judges and researchers · Study details (expand)",
        "academic_heading": "Research basis",
        "academic_values": (
            "**M2: 0.680 → with paired-data availability: 0.733 → M3: 0.758**\n\n"
            "Availability increment: ΔC = 0.052 (95% CI: 0.023–0.082)  \n"
            "Additional increment from ECog scores: ΔC = 0.026 (95% CI: 0.007–0.045)"
        ),
        "acoustic_heading": "Basis for the acoustic metrics",
        "acoustic_note": (
            "The pause ratio, pause duration and pitch variability (F0 SD) shown in "
            "the speech panel follow the vocal digital phenotype validated in the "
            "landmark study below: acoustic and linguistic features of narrative "
            "speech distinguish Alzheimer's disease, with pause and speech-rate "
            "features among the strongest predictors."
        ),
    },
}


def _copy(key: str) -> str:
    return _USER_COPY[get_ui_language()][key]


def main() -> None:
    render_brand(tr("dashboard_brand"))
    st.page_link(
        "modules/home.py",
        label=tr("back_home"),
        icon=":material/chat:",
    )
    st.markdown(
        """
        <style>
        .research-hero {
            padding: clamp(1.4rem, 4vw, 2.6rem);
            border: 1px solid #d3e3eb;
            border-radius: 1.4rem;
            background: linear-gradient(135deg, #e8f4f7 0%, #ffffff 70%);
            box-shadow: 0 16px 38px rgba(28, 64, 86, 0.09);
        }
        .research-hero h1 {
            margin: 0 0 0.8rem;
            color: #17364e;
            font-size: clamp(2rem, 5vw, 3.2rem);
            line-height: 1.15;
        }
        .research-hero p {
            max-width: 850px;
            margin: 0;
            color: #38576b;
            font-size: clamp(1.1rem, 2vw, 1.35rem);
            line-height: 1.7;
        }
        .research-slogan {
            margin: 1.8rem 0 0.5rem;
            color: #126c5e;
            font-size: clamp(1.65rem, 3.5vw, 2.4rem);
            font-weight: 800;
            line-height: 1.25;
        }
        .research-scale-note {
            color: #526d80;
            font-size: 1rem;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<section class="research-hero"><h1>{_copy("title")}</h1>'
        f'<p>{_copy("story")}</p></section>'
        f'<div class="research-slogan">{_copy("slogan")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(_copy("scale"))
    for value, key in (
        (68, "step_base"),
        (73, "step_availability"),
        (76, "step_ecog"),
    ):
        st.progress(value, text=_copy(key))
    st.markdown(f'<p class="research-scale-note">{_copy("caveat")}</p>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"### {_copy('analogy_title')}")
        st.write(_copy("analogy"))

    with st.expander(_copy("academic_toggle"), expanded=False):
        st.markdown(f"### {_copy('academic_heading')}")
        st.markdown(PAPER_CITATION)
        st.markdown(f"[{tr('paper_link')}]({PAPER_DOI})")
        st.markdown(_copy("academic_values"))
        st.plotly_chart(
            build_c_index_figure(),
            width="stretch",
            config={"displayModeBar": False, "responsive": True},
            key="c_index_decomposition",
        )
        st.caption(tr("rounding_note"))
        st.write(tr("paper_summary"))
        st.divider()
        st.markdown(f"### {_copy('acoustic_heading')}")
        st.markdown(ACOUSTIC_PAPER_CITATION)
        st.markdown(f"[{tr('paper_link')}]({ACOUSTIC_PAPER_DOI})")
        st.write(_copy("acoustic_note"))


if __name__ == "__main__":
    main()
