import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =========================================================
# 1. CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="AI Impact Analysis Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. GIAO DIỆN TRANG (CSS)
# =========================================================
st.markdown("""
    <style>
    /* Sử dụng biến theme của Streamlit để tự động đảo màu nền/chữ */
    .stApp { 
        background-color: var(--background-color); 
        color: var(--text-color); 
    }
    
    /* Thanh điều hướng bên cạnh: Giữ màu tối nhưng chữ theo biến hệ thống */
    [data-testid="stSidebar"] { 
        background-color: var(--secondary-background-color); 
    }
    [data-testid="stSidebar"] .stMarkdown { 
        color: var(--text-color); 
    }
    
    /* Khối tiêu đề chính */
    .header-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        padding: 35px 40px; border-radius: 16px; margin-bottom: 30px;
    }
    .main-title { font-size: 26px; font-weight: bold; color: #FFFFFF; }
    .sub-title { font-size: 14px; color: #93C5FD; font-weight: 400; }
    
    /* Khối Cards: Sử dụng màu nền phụ của Streamlit thay vì màu trắng cố định */
    .custom-card {
        background-color: var(--secondary-background-color);
        padding: 24px; border-radius: 16px;
        border: 1px solid var(--primary-color);
        margin-bottom: 25px;
    }
    .card-title { 
        font-size: 16px; font-weight: bold; color: var(--text-color); 
        margin-bottom: 20px; border-left: 4px solid #2563EB; padding-left: 12px;
    }
    
    /* Thẻ chỉ số phụ */
    .task-card {
        background-color: var(--background-color); 
        padding: 15px; border-radius: 12px;
        border: 1px solid var(--text-color);
    }
    .task-card-value { font-size: 26px; color: var(--text-color); font-weight: 800; }
    
    /* Tối ưu Tabs của Streamlit */
    .stTabs [data-baseweb="tab"] {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { 
        background-color: #2563EB !important; color: white !important; 
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. DỮ LIỆU & MAPPING CHUẨN HÓA
# =========================================================
raw_translation = {
    'Web Administrators': 'Quản trị viên Hệ thống Web',
    'Web Developers': 'Lập trình viên Web',
    'Computer User Support Specialists': 'Chuyên viên Hỗ trợ Người dùng Máy tính',
    'Computer Programmers': 'Lập trình viên Máy tính',
    'Database Administrators': 'Quản trị viên Cơ sở Dữ liệu',
    'Software Quality Assurance Analysts and Testers': 'Kỹ sư Kiểm thử & Đảm bảo Chất lượng',
    'Computer Network Support Specialists': 'Chuyên viên Hỗ trợ Mạng Máy tính',
    'Network and Computer Systems Administrators': 'Quản trị viên Hệ thống Mạng',
    'Computer Systems Analysts': 'Chuyên viên Phân tích Hệ thống',
    'Computer Systems Engineers/Architects': 'Kỹ sư/Kiến trúc sư Hệ thống',
    'Information Security Analysts': 'Chuyên viên Phân tích An ninh Thông tin',
    'Computer and Information Research Scientists': 'Nhà khoa học Nghiên cứu Máy tính',
    'Computer and Information Systems Managers': 'Quản lý Hệ thống Máy tính',
    'Information Technology Project Managers': 'Quản lý Dự án CNTT',
    'Video Game Designers': 'Nhà Thiết kế Trò chơi Điện tử'
}

selectbox_labels = {eng: f"💼 {eng} ({vie})" for eng, vie in raw_translation.items()}

task_translation = {
    "Update web code to accommodate changing graphics, features, or user requirements.": "Cập nhật mã nguồn trang web khi có thay đổi về đồ họa, tính năng hoặc yêu cầu từ người dùng",
    "Test web code to ensure it is valid, properly structured, and compatible with various browsers, devices, or operating systems.": "Kiểm tra mã nguồn để đảm bảo nó hợp lệ, được cấu trúc đúng cú pháp và tương thích với trình duyệt/thiết bị",
    "Identify problems uncovered by testing or customer feedback and correct problems or refer problems to support personnel.": "Xác định các sự cố kỹ thuật thông qua phản hồi hoặc kiểm thử để tiến hành sửa lỗi",
    "Back up web site data for immediate recovery in case of system disruptive events.": "Sao lưu dữ liệu trang web định kỳ để phục vụ cho các phương án ứng phó sự cố",
    "Implement web site security measures, such as firewalls, encryption, or access controls.": "Triển khai các biện pháp bảo mật như tường lửa, mã hóa luồng dữ liệu hoặc kiểm soát truy cập",
    "Develop web site code using standard programming languages.": "Phát triển mã nguồn cho trang web bằng các ngôn ngữ lập trình tiêu chuẩn",
    "Analyze user needs to determine technical requirements.": "Phân tích nhu cầu của người dùng để xác định các yêu cầu kỹ thuật đối với hệ thống",
    "Evaluate web code to ensure optimization, clean structure, adherence to industry standards, and browser compatibility.": "Đánh giá mã nguồn trang web để đảm bảo tính tối ưu, cấu trúc mã sạch và tuân thủ tiêu chuẩn",
    "Document network configurations, server setups, or operational procedures.": "Tài liệu hóa các cấu hình cài đặt hệ thống mạng, thiết lập máy chủ hoặc quy trình vận hành"
}

# Mapping thu nhập dạng dictionary thay vì chuỗi if/elif — dễ đọc & dễ mở rộng hơn
INCOME_MAP = {
    '0-30K': 15,
    '30-60K': 45,
    '60-86K': 73,
    '86K-165K': 125,
    '165K-209K': 187,
    '209K-529K': 369,
    '529K+': 550,
}


def translate_task(eng_task):
    return task_translation.get(eng_task, eng_task)


def convert_income_to_number(inc_str):
    """Chuyển chuỗi khoảng thu nhập (vd '60-86K') sang số đại diện ($K)."""
    inc_str = str(inc_str)
    for key, value in INCOME_MAP.items():
        if key in inc_str:
            return value
    return 0


def classify_persona(llm_use_value):
    """Phân loại 1 dòng dữ liệu (từ domain_worker_metadata.csv) theo tần suất dùng AI để vẽ biểu đồ persona."""
    freq = str(llm_use_value).lower()
    if 'every day' in freq or 'every week' in freq:
        return 'Người tiên phong'
    elif 'never' in freq:
        return 'Người đứng ngoài'
    return 'Người thận trọng'


def persona_from_freq_choice(freq_choice):
    """
    Ánh xạ lựa chọn tần suất của người dùng ("Daily/Weekly/Occasionally/Never")
    sang ĐÚNG 3 nhóm persona đã được dùng để gắn nhãn cho toàn bộ dữ liệu thật
    trong domain_worker_metadata.csv (cột 'LLM Use in Work' -> classify_persona()).
    Đây là ánh xạ 1-1 giữa 2 cách diễn đạt cùng một tần suất, không phải luật suy đoán chủ quan.
    """
    if freq_choice in ["Daily", "Weekly"]:
        return "Người tiên phong"
    elif freq_choice == "Never":
        return "Người đứng ngoài"
    return "Người thận trọng"  # Occasionally


# Thang điểm quy đổi thái độ định tính -> số (1: rất tiêu cực - 5: rất tích cực với AI)
ATTITUDE_MAP = {
    'Strongly disagree': 1,
    'Somewhat disagree': 2,
    'Neither agree nor disagree': 3,
    'Somewhat agree': 4,
    'Strongly agree': 5,
}
# 3 câu hỏi thái độ thể hiện mức độ tích cực/tin tưởng vào AI trong công việc
TRUST_ATTITUDE_COLUMNS = ['AI Tedious Work Attitude', 'AI Job Importance Attitude', 'AI Daily Interest Attitude']

# Ánh xạ lựa chọn "Công việc dùng AI nhiều nhất" sang đúng cột dữ liệu thực tế tương ứng
TASK_COLUMN_MAP = {
    "Coding": "LLM Usage by Type - Coding",
    "Data Analysis": "LLM Usage by Type - Analysis",
    "Communication": "LLM Usage by Type - Communication",
    "Idea Generation": "LLM Usage by Type - Idea Generation",
}


@st.cache_data
def load_data():
    expert_df = pd.read_csv('expert_rated_technological_capability.csv')
    metadata_df = pd.read_csv('domain_worker_metadata.csv')
    desires_df = pd.read_csv('domain_worker_desires.csv')
    task_df = pd.read_csv('task_statement_with_metadata.csv')

    cs_expert = expert_df[expert_df['Occupation (O*NET-SOC Title)'].isin(raw_translation.keys())].copy()
    cs_expert['Selectbox_Label'] = cs_expert['Occupation (O*NET-SOC Title)'].map(selectbox_labels)

    cs_desires_raw = desires_df[desires_df['Occupation (O*NET-SOC Title)'].isin(raw_translation.keys())].copy()
    cs_desires_raw['Selectbox_Label'] = cs_desires_raw['Occupation (O*NET-SOC Title)'].map(selectbox_labels)

    agg_df = cs_expert.groupby('Occupation (O*NET-SOC Title)').agg(
        Mean_Automation=('Automation Capacity Rating', 'mean'),
        Mean_HumanAgency=('Human Agency Scale Rating', 'mean'),
        Total_Tasks=('Automation Capacity Rating', 'count')
    ).reset_index()
    agg_df['Phân Nhóm Rủi Ro'] = pd.cut(
        agg_df['Mean_Automation'], bins=[0, 3.0, 3.6, 5],
        labels=['🛡️ Vùng An Toàn', '⚖️ Vùng Trung Bình', '⚠️ Vùng Nguy Hiểm']
    )
    agg_df['Selectbox_Label'] = agg_df['Occupation (O*NET-SOC Title)'].map(selectbox_labels)

    return cs_expert, agg_df, metadata_df, cs_desires_raw, task_df


cs_expert_raw, cs_summary, metadata_df, cs_desires_raw, task_df = load_data()
metadata_df['Income_Numeric'] = metadata_df['Income'].astype(str).apply(convert_income_to_number)
metadata_df['Persona_Group'] = metadata_df['LLM Use in Work'].apply(classify_persona)
# Điểm tin cậy AI (1-5) tính trực tiếp từ 3 câu hỏi thái độ thật trong khảo sát
metadata_df['AI_Trust_Score'] = metadata_df[TRUST_ATTITUDE_COLUMNS].apply(
    lambda row: np.nanmean([ATTITUDE_MAP.get(v, np.nan) for v in row]), axis=1
)

# =========================================================
# 4. THANH BÊN (SIDEBAR) & HEADER
# =========================================================
with st.sidebar:
    st.markdown("<br><h3 style='color: white; margin-bottom: 0;'>🤖 AI Agent Board</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; font-size: 13px;'>Hệ thống Phân tích Khoa học & Thực trạng</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 **Gợi ý:** Di chuyển giữa các Tab để phân tích hồ sơ và thực trạng ứng dụng công nghệ thực tế.")

st.markdown("""
    <div class="header-container">
        <div class="main-title">BÁO CÁO TÁC ĐỘNG AI AGENT TRONG NGÀNH KHOA HỌC MÁY TÍNH</div>
        <div class="sub-title">Nền tảng BI Dashboard cao cấp mô phỏng rủi ro nhân sự và khảo sát cộng đồng thực tế</div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# 5. KHỞI TẠO TABS CHÍNH
# =========================================================
tab_corr, tab_main, tab_auto = st.tabs([
    "🔍 Thực trạng hành vi sử dụng AI",
    "📈 Dự đoán mức thu nhập",
    "📊 Khả Năng Tự Động Hóa & Rủi ro",
])

EXP_SORT_ORDER = ['Less than 1 year', '1-2 year', '3-5 years', '6-10 years', 'More than 10 years']
INCOME_SORT_ORDER = ['0-30K', '30-60K', '60-86K', '86K-165K', '165K-209K', '209K-529K', '529K+']

# =========================================================
# TAB 2: TRỢ LÝ ẢO + DỰ ĐOÁN THU NHẬP
# =========================================================
with tab_main:
    # --- 5.1. FORM TRỢ LÝ ẢO ---
    st.markdown('<div class="card-title">🤖 Trợ Lý Ảo Cố Vấn Tối Ưu Thu Nhập & Kỹ Năng</div>', unsafe_allow_html=True)
    st.markdown("Vui lòng cung cấp thông tin hiện tại của bạn để hệ thống đối chiếu với dữ liệu thị trường và đưa ra chiến lược phù hợp.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        default_idx = next((i for i, label in enumerate(cs_summary['Selectbox_Label']) if "Computer Systems Analysts" in label), 0)
        user_occ_main = st.selectbox("Vị trí công việc:", options=cs_summary['Selectbox_Label'], index=default_idx, key="main_occ")
        occ_eng_main = [eng for eng, label in selectbox_labels.items() if label == user_occ_main][0]
    with c2:
        user_exp_main = st.selectbox("Kinh nghiệm:", options=EXP_SORT_ORDER, key="main_exp")
    with c3:
        user_salary = st.number_input("Thu nhập hiện tại ($K/năm):", min_value=0, max_value=1000, value=60, step=5, key="main_salary")
    with c4:
        user_ai_main = st.selectbox("Tần suất dùng AI:", options=["Daily", "Weekly", "Occasionally", "Never"], key="main_ai")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 5.2. LỌC & TÍNH TOÁN DỮ LIỆU ĐỐI CHIẾU ---
    # Dữ liệu rộng (cho biểu đồ tổng quan bên dưới)
    peers_df = metadata_df[metadata_df['Occupation (O*NET-SOC Title)'] == occ_eng_main].copy()
    is_fallback = False
    if len(peers_df) < 5:
        peers_df = metadata_df[metadata_df['Occupation (O*NET-SOC Title)'].isin(raw_translation.keys())].copy()
        is_fallback = True

    # Dữ liệu hẹp (bắt buộc đúng mốc kinh nghiệm, không dùng dự phòng)
    exact_peers_df = metadata_df[
        (metadata_df['Occupation (O*NET-SOC Title)'] == occ_eng_main) &
        (metadata_df['Experience'] == user_exp_main)
    ].copy()
    exact_peers_df['Income_Numeric'] = exact_peers_df['Income'].astype(str).apply(convert_income_to_number)

    ai_users = exact_peers_df[exact_peers_df['LLM Use in Work'].astype(str).str.contains('every day|every week', case=False, na=False)]
    non_ai_users = exact_peers_df[~exact_peers_df['LLM Use in Work'].astype(str).str.contains('every day|every week', case=False, na=False)]

    wage_data = task_df[task_df['Occupation (O*NET-SOC Title)'] == occ_eng_main]
    avg_wage = wage_data['Occupation Mean Annual Wage'].mean() if not wage_data.empty else 0
    display_wage = avg_wage / 1000

    avg_ai_salary = ai_users['Income_Numeric'].mean() if not ai_users.empty else 0
    avg_non_ai_salary = non_ai_users['Income_Numeric'].mean() if not non_ai_users.empty else 0
    avg_peer_salary = exact_peers_df['Income_Numeric'].mean() if not exact_peers_df.empty else 0
    occ_risk = cs_summary[cs_summary['Occupation (O*NET-SOC Title)'] == occ_eng_main]['Mean_Automation'].values[0]

    # --- 5.3. HIỂN THỊ METRIC ---
    rm1, rm2, rm3, rm4 = st.columns(4)
    with rm1:
        st.metric("Lương TB Ngành", f"${display_wage:,.1f}K")
    with rm2:
        st.metric("Thu nhập của bạn", f"${user_salary}K")
    with rm3:
        delta_ai = avg_ai_salary - user_salary
        st.metric("TBU nhóm Dùng AI", f"${avg_ai_salary:.1f}K", f"{delta_ai:.1f}K so với bạn", delta_color="normal" if delta_ai > 0 else "inverse")
    with rm4:
        delta_non_ai = avg_non_ai_salary - user_salary
        st.metric("TBU nhóm Ít/Không dùng", f"${avg_non_ai_salary:.1f}K", f"{delta_non_ai:.1f}K so với bạn", delta_color="normal" if delta_non_ai > 0 else "inverse")

    st.markdown("---")

    # --- 5.4. XÂY DỰNG LỜI KHUYÊN ---
    is_frequent_user = user_ai_main in ["Daily", "Weekly"]

    if is_frequent_user:
        benchmark_salary = avg_ai_salary if avg_ai_salary > 0 else avg_peer_salary
        group_name = "nhóm đồng nghiệp THƯỜNG XUYÊN DÙNG AI"
    else:
        benchmark_salary = avg_non_ai_salary if avg_non_ai_salary > 0 else avg_peer_salary
        group_name = "nhóm đồng nghiệp ÍT/KHÔNG DÙNG AI"

    is_high_salary = user_salary >= benchmark_salary
    salary_status = "cao hơn hoặc bằng" if is_high_salary else "đang thấp hơn"

    advice = f"**1. Vị thế thu nhập & Ứng dụng AI:** Mức lương của bạn {salary_status} mức trung bình của {group_name} cùng hạng cân (${benchmark_salary:.1f}K). \n\n"

    ai_pays_off = avg_ai_salary > avg_non_ai_salary

    if ai_pays_off:
        # TRƯỜNG HỢP 1: Nhóm dùng AI có lương CAO HƠN
        if is_frequent_user:
            if user_salary < avg_non_ai_salary:
                advice += "Mức lương của bạn đang thấp hơn cả nhóm không dùng AI. Điều này có nghĩa là bạn đang dùng AI mà lương bạn còn thấp hơn người làm thủ công. **Khuyến nghị:** Bạn đang lạm dụng AI sai cách hoặc chuyên môn lõi của bạn đang quá yếu. Hãy đánh giá lại cách làm việc và củng cố nền tảng nghiệp vụ."
            elif user_salary < avg_ai_salary:
                advice += "Mức lương của bạn cao hơn nhóm không dùng AI nhưng vẫn thấp hơn trung bình nhóm có dùng AI. **Khuyến nghị:** Bạn đang phối hợp và ứng dụng AI khá tốt! Hãy tiếp tục tối ưu hóa các prompt và học cách tự động hóa các tác vụ phức tạp hơn để bứt phá lên nhóm trên."
            else:
                advice += "Thu nhập của bạn đang bằng hoặc vượt mức trung bình của nhóm dùng AI. **Khuyến nghị:** Xin chúc mừng! Bạn chính là người dẫn đầu trong việc kết hợp chuyên môn và công nghệ. Hãy tiếp tục phát triển và duy trì vị thế tiên phong này."
        else:  # Không dùng AI
            if user_salary < avg_non_ai_salary:
                advice += "Mức lương của bạn đang thấp hơn cả hai nhóm. **Khuyến nghị:** Bạn vừa chưa có lợi thế chuyên môn, vừa cứng nhắc trong việc từ chối công cụ mới. Cần ngay lập tức học cách sử dụng AI cho các việc lặp đi lặp lại để giải phóng thời gian trau dồi nghiệp vụ."
            elif user_salary < avg_ai_salary:
                advice += "Bạn có thu nhập tốt hơn nhóm làm thủ công, nhưng vẫn thua nhóm biết tận dụng công nghệ. **Khuyến nghị:** Bạn đang có nền tảng rất tốt, hãy mở lòng học cách dùng AI ngay để tăng mức thu nhập của mình lên sánh ngang với nhóm dẫn đầu."
            else:
                advice += "Thu nhập của bạn vượt cả nhóm dùng AI dù bạn làm hoàn toàn thủ công. **Khuyến nghị:** Rất xuất sắc! Bạn là kiểu người không cần AI mà vẫn làm cực kỳ tốt nhờ tư duy và chuyên môn vượt trội. Tuy nhiên, thêm AI sẽ như mọc thêm cánh, hãy cứ thử nghiệm nhé."
    else:
        # TRƯỜNG HỢP 2: Nhóm dùng AI có lương THẤP HƠN (hoặc bằng)
        if is_frequent_user:
            if user_salary < avg_ai_salary:
                advice += "Mức lương của bạn đang thấp hơn cả hai nhóm. **Khuyến nghị:** Dường như việc dùng AI chưa giúp ích được gì, thậm chí làm bạn xao nhãng. Hãy cải thiện lại cách sử dụng AI sao cho đúng trọng tâm và mang lại giá trị thực tế hơn."
            elif user_salary < avg_non_ai_salary:
                advice += "Lương của bạn cao hơn mặt bằng nhóm dùng AI nhưng lại thấp hơn nhóm làm thủ công. **Khuyến nghị:** Ở mốc kinh nghiệm này, thị trường trả tiền cho chuyên môn. Hãy bớt thời gian cho công cụ lại và tập trung cải thiện phần chuyên môn sâu."
            else:
                advice += "Bất chấp xu hướng thị trường, bạn vẫn dùng AI và vươn lên trên cả nhóm không dùng AI. **Khuyến nghị:** Rất ấn tượng! Bạn là một trong số ít người thực sự biết cách ứng dụng AI khôn ngoan để phục vụ cho khối óc xuất sắc của mình."
        else:  # Không dùng AI
            if user_salary < avg_ai_salary:
                advice += "Mức lương của bạn đang thấp hơn cả nhóm dùng AI vốn đã có mặt bằng lương thấp. **Khuyến nghị:** Bạn đang gặp bất lợi kép: Vừa không có chuyên môn sâu, vừa cứng nhắc. Cần lập tức học hỏi trau dồi nghiệp vụ và thay đổi cách làm việc."
            elif user_salary < avg_non_ai_salary:
                advice += "Bạn đang có thu nhập ổn hơn nhóm lạm dụng AI, nhưng chưa chạm tới đỉnh của nhóm đi theo hướng chuyên môn sâu. **Khuyến nghị:** Trình độ chuyên môn của bạn ở mức khá ổn định. Cần phát huy thêm và học hỏi từ những người đi trước."
            else:
                advice += "Thu nhập của bạn thuộc nhóm dẫn đầu, hoàn toàn dựa vào năng lực cốt lõi. **Khuyến nghị:** Xin chúc mừng! Bạn là kiểu người có trình độ chuyên môn cực kỳ cao, giá trị của bạn nằm ở tư duy sắc bén chứ không phụ thuộc vào công cụ."

    advice += "\n\n**2. Rủi ro thay thế:** "
    if occ_risk >= 3.6:
        advice += "⚠️ Tác vụ lõi của ngành này có rủi ro bị AI tự động hóa cao. Bắt buộc phải tiến hóa thành người 'quản lý AI' thay vì làm thợ."
    elif occ_risk >= 3.0:
        advice += "⚖️ Công việc có khả năng bị tự động hóa một phần. Hãy tập trung mài giũa các kỹ năng mềm, xử lý ngoại lệ và tư duy hệ thống."
    else:
        advice += "🛡️ Nghề nghiệp của bạn đang rất an toàn. Hãy thoải mái dùng AI như một trợ lý đắc lực."

    st.info(advice)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 5.5. THỰC TRẠNG CỘNG ĐỒNG (BIỂU ĐỒ) ---
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Dữ Liệu Thực Tế Thị Trường (Dẫn chứng cho lời khuyên)</div>', unsafe_allow_html=True)

    if is_fallback:
        st.warning("⚠️ Số lượng khảo sát riêng của ngành này khá ít, dữ liệu biểu đồ dưới đây là gộp của toàn nhóm ngành Khoa học Máy tính.")
    else:
        st.success(f"Biểu đồ minh họa từ {len(peers_df)} nhân sự đang làm việc trong toàn bộ các cấp bậc của ngành '{raw_translation[occ_eng_main]}'.")

    peers_df['Income_Numeric'] = peers_df['Income'].astype(str).apply(convert_income_to_number)
    bar_df = peers_df[peers_df['Income'] != 'Prefer not to say'].copy()
    bar_df['Experience'] = pd.Categorical(bar_df['Experience'], categories=EXP_SORT_ORDER, ordered=True)
    bar_df['Income'] = pd.Categorical(bar_df['Income'], categories=INCOME_SORT_ORDER, ordered=True)
    bar_df['AI_Usage'] = bar_df['LLM Use in Work'].apply(
        lambda x: "Biết & Dùng AI thường xuyên (Daily/Weekly)" if ("every day" in str(x) or "every week" in str(x)) else "Hiếm khi / Không dùng AI"
    )
    chart_data = bar_df.groupby(['Experience', 'AI_Usage'], observed=False)['Income_Numeric'].mean().reset_index().dropna()

    fig_compare = px.bar(
        chart_data, x='Experience', y='Income_Numeric', color='AI_Usage', barmode='group', text_auto='.0f',
        labels={'Experience': 'Số năm kinh nghiệm', 'Income_Numeric': 'Lương trung bình ($K USD)', 'AI_Usage': 'Công nghệ:'},
        color_discrete_map={'Biết & Dùng AI thường xuyên (Daily/Weekly)': '#1E3A8A', 'Hiếm khi / Không dùng AI': '#94A3B8'},
        category_orders={"Experience": EXP_SORT_ORDER, "AI_Usage": ["Biết & Dùng AI thường xuyên (Daily/Weekly)", "Hiếm khi / Không dùng AI"]}
    )
    fig_compare.update_layout(template='plotly_white', height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.plotly_chart(fig_compare, use_container_width=True, key="combined_bar")

# =========================================================
# TAB 3: KHẢ NĂNG TỰ ĐỘNG HÓA & RỦI RO
# =========================================================
with tab_auto:
    # --- 6.1. BỘ LỌC ---
    st.markdown('<div class="card-title">🎛️ Phân Tích & Điểm Mù Thị Trường</div>', unsafe_allow_html=True)
    c_sel1, c_sel2, c_sel3 = st.columns(3)

    with c_sel1:
        selected_occ_label = st.selectbox("Chọn vị trí:", options=cs_summary['Selectbox_Label'].iloc[::-1], key="sb_tab_auto_occ")
    with c_sel2:
        filtered_by_occ = cs_expert_raw[cs_expert_raw['Selectbox_Label'] == selected_occ_label]
        task_options = {translate_task(t): t for t in filtered_by_occ['Task'].unique()}
        selected_task_vn = st.selectbox("Chọn tác vụ:", options=["✨ TẤT CẢ TÁC VỤ"] + list(task_options.keys()), key="sb_tab_auto_task")
    with c_sel3:
        user_automation_desire = st.slider(
            "Mong muốn tự động hóa:", min_value=0.0, max_value=5.0, value=2.5, step=0.1,
            key="slider_auto_desire", help="Mức độ bạn muốn AI can thiệp (0: Thủ công - 5: Tự động hoàn toàn)"
        )

    # --- 6.2. TÍNH TOÁN TỔNG HỢP (chỉ một lần, dùng lại cho toàn bộ tab) ---
    exp_auto = filtered_by_occ['Automation Capacity Rating'].mean()
    exp_agency = filtered_by_occ['Human Agency Scale Rating'].mean()

    des_data = cs_desires_raw[cs_desires_raw['Selectbox_Label'] == selected_occ_label]
    if selected_task_vn != "✨ TẤT CẢ TÁC VỤ":
        des_data = des_data[des_data['Task'] == task_options[selected_task_vn]]

    avg_data = des_data[des_data['Self-reported Expertise'] == 'Average']
    nov_data = des_data[des_data['Self-reported Expertise'] == 'Novice']

    avg_auto = avg_data['Automation Desire Rating'].mean() if not avg_data.empty else 0.0
    avg_ha = avg_data['Human Agency Scale Rating'].mean() if not avg_data.empty else 0.0
    nov_auto = nov_data['Automation Desire Rating'].mean() if not nov_data.empty else 0.0
    nov_ha = nov_data['Human Agency Scale Rating'].mean() if not nov_data.empty else 0.0

    risky_tasks_df = filtered_by_occ[
        (filtered_by_occ['Automation Capacity Rating'] >= 3.5) &
        (filtered_by_occ['Human Agency Scale Rating'] <= 2.5)
    ].drop_duplicates(subset=['Task'])
    risky_tasks = risky_tasks_df['Task'].tolist()

    # --- 6.3. KẾT LUẬN THEO MONG MUỐN CÁ NHÂN ---
    st.markdown('<div class="card-title">🎯 Kết luận & Khuyến nghị chiến lược</div>', unsafe_allow_html=True)

    if user_automation_desire > exp_auto:
        st.warning(f"""
        ⚠️ **CẢNH BÁO MỨC ĐỘ KỲ VỌNG:** Mức độ tự động hóa bạn mong muốn ({user_automation_desire:.1f}) 
        đang **cao hơn đáng kể** so với khả năng thực tế mà AI có thể đảm nhận một cách an toàn trong ngành này (Điểm: {exp_auto:.1f}).
        
        👉 **Lời khuyên:** Công nghệ hiện tại chưa đáp ứng được kỳ vọng tự động hóa cao như vậy. 
        Đề xuất bạn nên tập trung **trau dồi thêm chuyên môn sâu**, vì trong các tác vụ phức tạp này, 
        sự can thiệp và tư duy của con người vẫn là yếu tố then chốt để đảm bảo chất lượng.
        """)
    else:
        st.success(f"""
        ✅ **HỢP LÝ:** Mức độ mong muốn tự động hóa của bạn ({user_automation_desire:.1f}) 
        nằm trong ngưỡng an toàn và khả thi mà AI có thể hỗ trợ (Khả năng AI: {exp_auto:.1f}).
        
        👉 **Lời khuyên:** Tiếp tục áp dụng mô hình 'AI hỗ trợ' (Assistant) để tối ưu hiệu suất công việc hiện tại.
        """)

    # --- 6.4. DỮ LIỆU THỰC TẾ THỊ TRƯỜNG + ĐIỂM MÙ (Tech Resistance / Lazy Novice) ---
    st.markdown('<div class="card-title">📊 Dữ Liệu Thực Tế Thị Trường (Dẫn chứng cho lời khuyên)</div>', unsafe_allow_html=True)

    insight_found = False
    if exp_auto >= 3.5 and avg_auto <= 2.5:
        st.error("**⚠️ CẢNH BÁO: KHÁNG CỰ CÔNG NGHỆ (Tech Resistance)**")
        insight_found = True
    elif nov_auto >= 3.8 and exp_auto <= 2.5:
        st.warning("**⚠️ CẢNH BÁO: ẢO TƯỞNG SỨC MẠNH (The Lazy Novice)**")
        insight_found = True
    if not insight_found:
        st.success("✅ Trạng thái cân bằng.")

    chart_data = pd.DataFrame({
        'Nhóm': ['Chuyên gia', 'Trung bình (Avg)', 'Mới (Novice)'],
        'Tự động hóa': [exp_auto, avg_auto, nov_auto],
        'Quyền con người': [exp_agency, avg_ha, nov_ha]
    })
    df_melted = chart_data.melt(id_vars='Nhóm', var_name='Chỉ số', value_name='Điểm số')

    fig_comp = px.bar(
        df_melted, x='Chỉ số', y='Điểm số', color='Nhóm',
        barmode='group',
        color_discrete_map={'Chuyên gia': '#1E3A8A', 'Trung bình (Avg)': '#F59E0B', 'Mới (Novice)': '#10B981'},
        template='plotly_white'
    )
    st.plotly_chart(fig_comp, use_container_width=True, key="grouped_bar_comparison")

    # --- 6.5. KẾT LUẬN & CHIẾN LƯỢC SỬ DỤNG AI (THEO NGÀNH TỔNG THỂ) ---
    st.markdown("---")
    st.markdown('<div class="card-title">🎯 Kết luận & Chiến lược sử dụng AI</div>', unsafe_allow_html=True)

    if exp_auto >= 3.5 and exp_agency <= 2.5:
        st.error(f"""
        ⚠️ **CẢNH BÁO RỦI RO BỊ THAY THẾ:** Các tác vụ trong ngành này có mức độ tự động hóa rất cao (Điểm: {exp_auto:.1f}) 
        trong khi quyền quyết định của con người rất hạn chế (Agency: {exp_agency:.1f}). 
        **Hãy sử dụng AI một cách có chiến lược.**
        """)
    elif exp_auto >= 3.0 and exp_agency <= 3.0:
        st.warning(f"""
        ⚖️ **CẢNH BÁO TRUNG BÌNH:** Ngành này đang dần tự động hóa (Điểm: {exp_auto:.1f}). Dù con người vẫn có quyền quyết định (Agency: {exp_agency:.1f}), 
        nhưng bạn cần nâng cao kỹ năng sử dụng công cụ AI để duy trì lợi thế cạnh tranh.
        """)
    else:
        st.success("✅ **TRẠNG THÁI AN TOÀN:** Ngành của bạn vẫn yêu cầu sự tham gia và sáng tạo cao từ con người. AI hiện tại chỉ đóng vai trò hỗ trợ.")

    # --- 6.6. CẢNH BÁO CÁC TÁC VỤ RỦI RO CAO ---
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🚨 Cảnh báo về AI thay thế</div>', unsafe_allow_html=True)

    if risky_tasks:
        st.warning(f"⚠️ **CẢNH BÁO:** Có **{len(risky_tasks)} tác vụ** trong ngành này có nguy cơ cao bị thay thế do AI đảm nhận toàn bộ quyền kiểm soát.")
        for task in risky_tasks:
            st.markdown(f"- 🚩 **{translate_task(task)}**")
        st.info("💡 **Lời khuyên:** Đây là các tác vụ mà AI đã làm chủ (Automation cao) và con người ít can thiệp (Agency thấp). Hãy tập trung nâng cao kỹ năng tư duy phản biện và quản lý hệ thống AI để không trở thành người bị thay thế.")
    else:
        st.success("✅ Ngành này vẫn duy trì sự cân bằng tốt giữa quyền con người và khả năng tự động hóa.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 6.7. BIỂU ĐỒ SCATTER TỔNG QUAN NGÀNH NGHỀ ---
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🌐 Phân bố rủi ro ngành nghề</div>', unsafe_allow_html=True)

    fig_scatter = px.scatter(
        cs_summary,
        x='Mean_Automation',
        y='Mean_HumanAgency',
        size='Total_Tasks',
        color='Phân Nhóm Rủi Ro',
        hover_name='Occupation (O*NET-SOC Title)',
        text='Occupation (O*NET-SOC Title)',
        color_discrete_map={
            '🛡️ Vùng An Toàn': '#10B981',
            '⚖️ Vùng Trung Bình': '#F59E0B',
            '⚠️ Vùng Nguy Hiểm': '#EF4444'
        },
        template='plotly_white',
        height=600
    )
    fig_scatter.update_traces(textposition='top center', textfont_size=10)
    fig_scatter.update_layout(xaxis_title="Automation Capacity", yaxis_title="Human Agency")

    st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_risk_zones_en")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TAB 1: THỰC TRẠNG HÀNH VI SỬ DỤNG AI (AI PERSONA PREDICTOR)
# =========================================================
with tab_corr:
    st.markdown('<div class="card-title">🔍 AI Persona Predictor: Bạn là ai trong kỷ nguyên số?</div>', unsafe_allow_html=True)

    # --- 7.1. Ô ĐIỀN THÔNG TIN (INPUT) ---
    col1, col2 = st.columns(2)
    with col1:
        user_freq = st.selectbox("Tần suất sử dụng AI:", ["Daily", "Weekly", "Occasionally", "Never"])
        user_tasks = st.multiselect("Công việc bạn dùng AI nhiều nhất:",
                                     ["Coding", "Data Analysis", "Communication", "Idea Generation"])
    with col2:
        user_attitude = st.slider("Mức độ tin tưởng vào AI (1-5):", 1, 5, 3)

    # --- 7.2. PHÂN LOẠI NHÓM DỰA TRÊN DỮ LIỆU THẬT (domain_worker_metadata.csv) ---
    # Không dùng luật suy đoán chủ quan: persona được xác định bằng đúng cách phân
    # nhóm đã áp dụng cho toàn bộ 1500 người trong file (cột 'LLM Use in Work'),
    # sau đó mọi số liệu đi kèm đều là số liệu thật đo được trên nhóm đó.
    if st.button("Xác định nhóm của bạn"):
        persona = persona_from_freq_choice(user_freq)
        peer_segment = metadata_df[metadata_df['Persona_Group'] == persona]

        peer_count = len(peer_segment)
        peer_pct = peer_count / len(metadata_df) * 100
        peer_avg_income = peer_segment['Income_Numeric'].mean()
        peer_avg_trust = peer_segment['AI_Trust_Score'].mean()

        st.success(f"Dựa trên dữ liệu khảo sát thực tế, bạn thuộc nhóm: **{persona}**")

        pm1, pm2, pm3 = st.columns(3)
        with pm1:
            st.metric("Số người cùng nhóm trong khảo sát", f"{peer_count} người", f"{peer_pct:.1f}% tổng mẫu")
        with pm2:
            st.metric("Thu nhập TB của nhóm", f"${peer_avg_income:.1f}K")
        with pm3:
            st.metric("Độ tin cậy TB vào AI của nhóm (thang 1-5)", f"{peer_avg_trust:.1f}", f"Bạn tự chấm: {user_attitude}")

        if user_tasks:
            st.markdown("**Tỷ lệ người cùng nhóm cũng dùng AI hàng ngày/hàng tuần cho các việc bạn chọn (theo dữ liệu thật):**")
            for task in user_tasks:
                col_name = TASK_COLUMN_MAP.get(task)
                if col_name and col_name in peer_segment.columns:
                    active_pct = peer_segment[col_name].isin(['Daily', 'Weekly']).mean() * 100
                    st.markdown(f"- **{task}**: {active_pct:.1f}%")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- 7.3. BIỂU ĐỒ DẪN CHỨNG: SO SÁNH THU NHẬP GIỮA 3 NHÓM ---
    st.markdown('<div class="card-title">📊 Dẫn chứng thực tế: Sự khác biệt thu nhập</div>', unsafe_allow_html=True)

    fig = px.bar(
        metadata_df.groupby('Persona_Group')['Income_Numeric'].mean().reset_index(),
        x='Persona_Group', y='Income_Numeric',
        color='Persona_Group',
        title="Thu nhập trung bình theo Chân dung người dùng (Dữ liệu thị trường)",
        color_discrete_map={'Người tiên phong': '#1E3A8A', 'Người thận trọng': '#F59E0B', 'Người đứng ngoài': '#94A3B8'}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 7.4. BIỂU ĐỒ SCATTER ĐỘ TUỔI & HỌC VẤN ---
    EDU_ORDER = ['High School', 'Some College, No Degree', 'Associate Degree', 'Bachelor’s Degree',
                 'Master’s Degree', 'Professional Degree (e.g., MD, JD)', 'Doctorate (e.g., PhD)']

    df_scatter = peers_df.copy()
    df_scatter['Education'] = pd.Categorical(df_scatter['Education'], categories=EDU_ORDER, ordered=True)
    df_scatter['AI_User_Group'] = df_scatter['LLM Use in Work'].apply(
        lambda x: "Thường xuyên sử dụng AI" if ("every day" in str(x) or "every week" in str(x)) else "Hiếm khi / Không sử dụng AI"
    )

    st.markdown('<div class="card-title">📊 Tương quan: Độ tuổi - Học vấn - AI</div>', unsafe_allow_html=True)
    fig_scatter = px.strip(
        df_scatter, x="Education", y="Age", color="AI_User_Group",
        color_discrete_map={"Thường xuyên sử dụng AI": "#1E3A8A", "Hiếm khi / Không sử dụng AI": "#BAE6FD"},
        labels={"Age": "Độ tuổi", "Education": "Trình độ học vấn"}
    )
    fig_scatter.update_traces(marker=dict(size=14, opacity=0.85, line=dict(width=0.5, color='white')), jitter=0.7)
    fig_scatter.update_layout(
        template='plotly_white', height=500,
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="Trình độ học vấn", categoryorder='array', categoryarray=EDU_ORDER),
        yaxis=dict(title="Độ tuổi", gridcolor='#F1F5F9')
    )
    st.plotly_chart(fig_scatter, use_container_width=True, key="combined_scatter")
    st.markdown('</div>', unsafe_allow_html=True)
