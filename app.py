import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
import io

# ---------------------------------------------------------
# SETUP PAGE & CUSTOM APPLE LIQUID GLASS CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Hệ thống Phát hiện Giao dịch Bất thường",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Apple's Liquid Glass (Glassmorphism) Aesthetic
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Main Background with Apple Space & Neon Glow */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(88, 28, 135, 0.15) 0%, rgba(15, 23, 42, 0.15) 50%, rgba(9, 9, 11, 1) 100%);
        background-attachment: fixed;
        color: #f1f5f9;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Sidebar styling - Liquid Glass */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Glossy Header text gradient */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #ffffff 40%, #c084fc 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: -0.02em;
    }
    
    /* Liquid Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(192, 132, 252, 0.3);
        box-shadow: 0 12px 40px 0 rgba(168, 85, 247, 0.15);
    }
    
    /* Glossy Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.7) 0%, rgba(79, 70, 229, 0.7) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: white !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.3) !important;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(147, 51, 234, 0.5) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        background: linear-gradient(135deg, rgba(147, 51, 234, 0.9) 0%, rgba(79, 70, 229, 0.9) 100%) !important;
    }
    
    /* Metrics display elements */
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 5px 0;
        letter-spacing: -0.03em;
    }
    
    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94a3b8;
    }
    
    .metric-emergency {
        color: #ef4444;
        text-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
    }
    
    .metric-warning {
        color: #f59e0b;
        text-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
    }
    
    .metric-normal {
        color: #10b981;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
    }
    
    /* File uploader customizing */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 2px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* Customize Streamlit widgets values and backgrounds */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Custom tab headers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(168, 85, 247, 0.2) !important;
        color: white !important;
        border-bottom: 2px solid #a855f7 !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# HELPER DATA LOADING & CACHING FUNCTIONS
# ---------------------------------------------------------
@st.cache_data
def load_data(uploaded_file=None):
    """Loads transaction data from uploaded file or local path."""
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            return df, "Uploaded File"
        except Exception as e:
            st.error(f"Lỗi khi đọc file upload: {e}")
            return None, None
    else:
        # Fallback to local csv
        local_path = "transactions_Q1_demo.csv"
        if os.path.exists(local_path):
            try:
                df = pd.read_csv(local_path)
                return df, "transactions_Q1_demo.csv"
            except Exception as e:
                st.error(f"Lỗi khi đọc file dữ liệu cục bộ: {e}")
                return None, None
        else:
            return None, None


@st.cache_data
def preprocess_data(df):
    """Processes features and prepares date columns, matching the notebook logic."""
    df_processed = df.copy()
    
    # Check date column
    if 'transaction_date' in df_processed.columns:
        df_processed['transaction_date'] = pd.to_datetime(df_processed['transaction_date'], errors='coerce')
        # Fill NaT if any
        df_processed['transaction_date'] = df_processed['transaction_date'].ffill().bfill()
        df_processed['hour'] = df_processed['transaction_date'].dt.hour
        df_processed['weekday'] = df_processed['transaction_date'].dt.dayofweek
        df_processed['is_weekend'] = (df_processed['weekday'] >= 5).astype(int)
        df_processed['is_night'] = ((df_processed['hour'] < 6) | (df_processed['hour'] > 22)).astype(int)
    else:
        # Default to hour 12 if missing
        df_processed['hour'] = 12
        df_processed['is_weekend'] = 0
        df_processed['is_night'] = 0
        
    # Check amount column
    if 'amount' not in df_processed.columns:
        df_processed['amount'] = 0.0
    df_processed['log_amount'] = np.log1p(df_processed['amount'])
    df_processed['is_round_million'] = (df_processed['amount'] % 1_000_000 == 0).astype(int)
    df_processed['is_round_billion'] = (df_processed['amount'] % 1_000_000_000 == 0).astype(int)
    
    # Check is_employee column
    if 'is_employee' in df_processed.columns:
        # Check if column is boolean/string and map accordingly
        df_processed['is_employee_int'] = df_processed['is_employee'].astype(int)
    else:
        df_processed['is_employee_int'] = 0
        
    # Check channel column
    if 'channel' in df_processed.columns:
        df_processed['channel_code'] = df_processed['channel'].astype('category').cat.codes
    else:
        df_processed['channel_code'] = 0
        
    return df_processed


@st.cache_resource
def train_model(X_scaled, n_estimators, contamination, random_state=42):
    """Trains the Isolation Forest model and caches the fit object."""
    iso = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1
    )
    iso.fit(X_scaled)
    return iso


# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg", width=50)
st.sidebar.title("Điều khiển & Cấu hình")

# 1. File Upload
st.sidebar.subheader("1. Nguồn Dữ Liệu")
uploaded_file = st.sidebar.file_uploader("Tải lên file giao dịch CSV mới", type=["csv"])

# 2. Hyperparameters
st.sidebar.subheader("2. Cấu hình mô hình")
n_estimators = st.sidebar.slider("Số lượng cây (n_estimators)", min_value=50, max_value=500, value=200, step=50)
contamination = st.sidebar.slider("Tỷ lệ bất thường giả định (contamination)", min_value=0.001, max_value=0.05, value=0.01, step=0.001, format="%.3f")
random_state = 42

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; color: #64748b; font-size: 0.8rem;'>
        <b>Hệ thống phát hiện giao dịch bất thường</b><br>
        Giao diện <i>Liquid Glass</i> của Apple<br>
        © 2026 DeepMind Pair Programming
    </div>
    """, 
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# DATA LOADING & INITIALIZATION
# ---------------------------------------------------------
raw_df, source_name = load_data(uploaded_file)

if raw_df is None:
    st.title("💎 Hệ thống Phát hiện Giao dịch Bất thường")
    st.error("Không tìm thấy file dữ liệu mẫu 'transactions_Q1_demo.csv' và chưa có file nào được tải lên sidebar!")
    st.info("Vui lòng kéo & thả tệp CSV giao dịch của bạn vào khung bên trái để bắt đầu.")
else:
    # Preprocess
    df_processed = preprocess_data(raw_df)
    
    # Target columns
    features = ['amount', 'hour', 'is_employee_int']
    
    # Scale features
    scaler = StandardScaler()
    X = df_processed[features]
    X_scaled = scaler.fit_transform(X)
    
    # Model execution
    iso_model = train_model(X_scaled, n_estimators, contamination, random_state)
    
    # Predictions
    df_processed['anomaly_score'] = iso_model.decision_function(X_scaled)
    df_processed['is_anomaly'] = iso_model.predict(X_scaled) == -1
    
    # Anomaly categorization
    df_anomalies = df_processed[df_processed['is_anomaly'] == True]
    num_anomalies = len(df_anomalies)
    
    if num_anomalies > 0:
        # Determine 25th percentile cutoff of anomaly scores of anomalies for emergency categorizing
        q25 = df_anomalies['anomaly_score'].quantile(0.25)
        # Assign risk level
        df_processed['risk_level'] = "Bình thường"
        df_processed.loc[(df_processed['is_anomaly'] == True) & (df_processed['anomaly_score'] >= q25), 'risk_level'] = "Cảnh báo"
        df_processed.loc[(df_processed['is_anomaly'] == True) & (df_processed['anomaly_score'] < q25), 'risk_level'] = "Khẩn cấp"
    else:
        df_processed['risk_level'] = "Bình thường"
        q25 = 0.0
        
    # Stats preparation
    total_txns = len(df_processed)
    emergency_txns = len(df_processed[df_processed['risk_level'] == "Khẩn cấp"])
    warning_txns = len(df_processed[df_processed['risk_level'] == "Cảnh báo"])
    normal_txns = total_txns - num_anomalies
    
    total_anomaly_amount = df_anomalies['amount'].sum() if num_anomalies > 0 else 0

    # ---------------------------------------------------------
    # APP HEADER
    # ---------------------------------------------------------
    st.title("💎 Hệ thống Phát hiện Giao dịch Bất thường")
    st.markdown(f"Đang hiển thị phân tích từ nguồn dữ liệu: `{source_name}` (Gồm {total_txns:,} giao dịch)")
    
    # ---------------------------------------------------------
    # MAIN DASHBOARD METRICS (Liquid Glass Columns)
    # ---------------------------------------------------------
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    with m_col1:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">Tổng giao dịch</div>
            <div class="metric-val">{total_txns:,}</div>
            <div style="color: #38bdf8; font-size: 0.85rem;">Phân tích quý Q1</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">Giao dịch bình thường</div>
            <div class="metric-val metric-normal">{normal_txns:,}</div>
            <div style="color: #64748b; font-size: 0.85rem;">Tỷ lệ: {normal_txns/total_txns:.2%}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">Giao dịch bất thường</div>
            <div class="metric-val metric-warning">{num_anomalies:,}</div>
            <div style="color: #64748b; font-size: 0.85rem;">Giả định rủi ro: {contamination:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col4:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">Rủi ro khẩn cấp</div>
            <div class="metric-val metric-emergency">{emergency_txns:,}</div>
            <div style="color: #64748b; font-size: 0.85rem;">25% điểm rủi ro cao nhất</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # INTERACTIVE TABS
    # ---------------------------------------------------------
    tab_overview, tab_visuals, tab_explorer, tab_tester = st.tabs([
        "📊 Tổng quan & Phân bổ", 
        "🌌 Trực quan 3D Không gian", 
        "🔍 Bộ lọc & Truy vấn", 
        "🧠 Trình kiểm tra giao dịch nhanh"
    ])
    
    # Tab 1: Overview and Distributions
    with tab_overview:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Số lượng giao dịch theo giờ (Bình thường vs Bất thường)")
            
            # Aggregate data for bar chart
            hour_stats = df_processed.groupby(['hour', 'is_anomaly']).size().reset_index(name='count')
            hour_stats['Trạng thái'] = hour_stats['is_anomaly'].map({False: 'Bình thường', True: 'Bất thường'})
            
            # Plotly stacked bar chart
            fig_hour = px.bar(
                hour_stats, 
                x='hour', 
                y='count', 
                color='Trạng thái',
                color_discrete_map={'Bình thường': '#0ea5e9', 'Bất thường': '#ec4899'},
                labels={'hour': 'Giờ Giao Dịch', 'count': 'Số lượng Giao Dịch'},
                barmode='group'
            )
            fig_hour.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8', family='Outfit'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickmode='linear'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', type='log' if st.checkbox("Log scale Trục Y", value=True, key="hour_log") else 'linear')
            )
            st.plotly_chart(fig_hour, use_container_width=True)
            
        with col_chart2:
            st.subheader("Phân bổ Điểm rủi ro (Anomaly Score)")
            
            # Plotly histogram of anomaly scores
            fig_score = px.histogram(
                df_processed,
                x='anomaly_score',
                color='risk_level',
                color_discrete_map={'Bình thường': '#10b981', 'Cảnh báo': '#f59e0b', 'Khẩn cấp': '#ef4444'},
                labels={'anomaly_score': 'Điểm Anomaly (Cao = Bình thường, Thấp = Rủi ro)', 'count': 'Tần suất', 'risk_level': 'Mức độ'},
                nbins=100
            )
            fig_score.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8', family='Outfit'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig_score, use_container_width=True)
            
        # Insights text
        st.markdown(f"""
        <div class="glass-card">
            <h4>💡 Nhận định phân tích hệ thống</h4>
            <ul>
                <li>Tổng lượng tiền nằm trong các giao dịch rủi ro phát hiện được là: <b>{total_anomaly_amount:,.2f} VND</b>.</li>
                <li>Điểm rủi ro (Anomaly Score) dao động từ <b>{df_processed['anomaly_score'].min():.4f}</b> đến <b>{df_processed['anomaly_score'].max():.4f}</b>.</li>
                <li>Ngưỡng phân chia giao dịch bất thường Khẩn cấp (Emergency) là điểm rủi ro nhỏ hơn <b>{q25:.4f}</b>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    # Tab 2: 3D Interactive Visualization
    with tab_visuals:
        st.subheader("Không gian 3D đặc trưng giao dịch (Interactive 3D Scatter Plot)")
        st.write("Dùng chuột giữ và kéo xoay biểu đồ, cuộn chuột để zoom không gian 3D.")
        
        # Plotly 3D scatter
        # Use log amount for plotting to handle wide scale (4000 to 2B) and prevent visual squeeze
        fig_3d = go.Figure()
        
        colors_map = {
            'Bình thường': 'rgba(16, 185, 129, 0.4)',
            'Cảnh báo': 'rgba(245, 158, 11, 0.8)',
            'Khẩn cấp': 'rgba(239, 68, 68, 0.95)'
        }
        
        # Add normal trace first
        normal_data = df_processed[df_processed['risk_level'] == 'Bình thường']
        fig_3d.add_trace(go.Scatter3d(
            x=normal_data['hour'],
            y=normal_data['amount'],
            z=normal_data['is_employee_int'],
            name='Bình thường',
            mode='markers',
            marker=dict(
                size=3,
                color='#10b981',
                opacity=0.3
            ),
            text=normal_data['transaction_id']
        ))
        
        # Add warning trace
        warning_data = df_processed[df_processed['risk_level'] == 'Cảnh báo']
        fig_3d.add_trace(go.Scatter3d(
            x=warning_data['hour'],
            y=warning_data['amount'],
            z=warning_data['is_employee_int'],
            name='Cảnh báo',
            mode='markers',
            marker=dict(
                size=6,
                color='#f59e0b',
                opacity=0.8,
                symbol='circle'
            ),
            text=warning_data['transaction_id']
        ))
        
        # Add emergency trace
        emergency_data = df_processed[df_processed['risk_level'] == 'Khẩn cấp']
        fig_3d.add_trace(go.Scatter3d(
            x=emergency_data['hour'],
            y=emergency_data['amount'],
            z=emergency_data['is_employee_int'],
            name='Khẩn cấp',
            mode='markers',
            marker=dict(
                size=8,
                color='#ef4444',
                opacity=0.95,
                symbol='diamond'
            ),
            text=emergency_data['transaction_id']
        ))
        
        fig_3d.update_layout(
            scene=dict(
                xaxis_title='Giờ Giao Dịch',
                yaxis_title='Số Tiền (VND)',
                zaxis_title='Nhân Viên (0=Khách, 1=NV)',
                yaxis=dict(
                    type='log' if st.checkbox("Log scale trục số tiền trong biểu đồ 3D", value=True, key="log_3d") else 'linear',
                    gridcolor='rgba(255,255,255,0.05)',
                    backgroundcolor='rgba(0,0,0,0)'
                ),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', backgroundcolor='rgba(0,0,0,0)'),
                zaxis=dict(gridcolor='rgba(255,255,255,0.05)', backgroundcolor='rgba(0,0,0,0)', dtick=1)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8', family='Outfit'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, b=0, t=30),
            height=650
        )
        st.plotly_chart(fig_3d, use_container_width=True)
        
    # Tab 3: Search & Export Explorer
    with tab_explorer:
        st.subheader("Bộ lọc truy vấn thông tin giao dịch")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_risk = st.selectbox("Lọc theo mức độ rủi ro", ["Tất cả", "Khẩn cấp", "Cảnh báo", "Bình thường"])
        with col_f2:
            search_query = st.text_input("Tìm kiếm theo Mã giao dịch (Transaction ID) hoặc Hash tài khoản")
        with col_f3:
            filter_emp = st.selectbox("Đối tượng giao dịch", ["Tất cả", "Khách hàng thông thường", "Nhân viên ngân hàng"])
            
        # Apply filters
        df_filtered = df_processed.copy()
        if filter_risk != "Tất cả":
            df_filtered = df_filtered[df_filtered['risk_level'] == filter_risk]
        if search_query:
            df_filtered = df_filtered[
                df_filtered['transaction_id'].str.contains(search_query, case=False, na=False) |
                df_filtered['customer_id_hash'].str.contains(search_query, case=False, na=False) |
                df_filtered['account_no_hash'].str.contains(search_query, case=False, na=False)
            ]
        if filter_emp != "Tất cả":
            emp_val = True if filter_emp == "Nhân viên ngân hàng" else False
            df_filtered = df_filtered[df_filtered['is_employee'] == emp_val]
            
        # Display table
        st.write(f"Tìm thấy **{len(df_filtered):,}** giao dịch phù hợp bộ lọc.")
        
        # Sort values
        df_display = df_filtered[[
            'transaction_id', 'transaction_date', 'customer_id_hash', 
            'account_no_hash', 'amount', 'transaction_type', 
            'channel', 'counterparty_bank', 'location', 
            'is_employee', 'anomaly_score', 'risk_level'
        ]].sort_values(by='anomaly_score', ascending=True)

        # Format amount for display
        df_display_show = df_display.copy()

        if 'amount' in df_display_show.columns:
            df_display_show['amount'] = df_display_show['amount'].apply(
                lambda x: f"{x:,.2f}" if pd.notnull(x) else ""
            )

        if 'anomaly_score' in df_display_show.columns:
            df_display_show['anomaly_score'] = df_display_show['anomaly_score'].apply(
                lambda x: f"{x:.5f}" if pd.notnull(x) else ""
            )

        st.dataframe(
            df_display_show,
            use_container_width=True,
            height=400
        )

        # Export buttons
        st.write("---")
        st.subheader("Xuất dữ liệu")
        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            csv_data = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải về tệp CSV đã lọc",
                data=csv_data,
                file_name="giao_dich_loc.csv",
                mime="text/csv",
                key="download_csv"
            )

        with col_exp2:
            # Excel export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_display.to_excel(writer, sheet_name='Giao dịch', index=False)
            st.download_button(
                label="📥 Tải về tệp Excel đã lọc",
                data=buffer.getvalue(),
                file_name="giao_dich_loc.xlsx",
                mime="application/vnd.ms-excel",
                key="download_excel"
            )
            
    # Tab 4: Real-time Single Transaction Tester
    with tab_tester:
        st.subheader("🧠 Trình kiểm tra & Chấm điểm giao dịch thời gian thực")
        st.write("Vui lòng nhập thông tin chi tiết của giao dịch cần kiểm tra rủi ro:")
        
        col_in1, col_in2, col_in3 = st.columns(3)
        with col_in1:
            test_amount = st.number_input("Số tiền giao dịch (VND)", min_value=0.0, value=1000000.0, step=100000.0)
        with col_in2:
            test_hour = st.slider("Giờ thực hiện giao dịch (0h - 23h)", min_value=0, max_value=23, value=12, step=1)
        with col_in3:
            test_emp = st.selectbox("Đối tượng thực hiện", ["Khách hàng (is_employee = False)", "Nhân viên (is_employee = True)"])
            
        btn_check = st.button("🔥 Bắt đầu kiểm tra rủi ro")
        
        if btn_check:
            # Convert inputs
            emp_val_int = 1 if "Nhân viên" in test_emp else 0
            
            # Construct input vector matching the exact feature columns
            input_data = pd.DataFrame([[test_amount, test_hour, emp_val_int]], columns=features)
            
            # Scale using the previously fitted scaler
            input_scaled = scaler.transform(input_data)
            
            # Predict
            pred_score = iso_model.decision_function(input_scaled)[0]
            is_anom_pred = iso_model.predict(input_scaled)[0] == -1
            
            # Assign risk label based on trained dataset cutoff
            if not is_anom_pred:
                pred_label = "Bình thường"
                status_class = "metric-normal"
                status_text = "🟢 Giao dịch bình thường (Rủi ro rất thấp)"
                gauge_color = "#10b981"
            elif pred_score >= q25:
                pred_label = "Cảnh báo"
                status_class = "metric-warning"
                status_text = "🟡 Cảnh báo bất thường (Rủi ro trung bình)"
                gauge_color = "#f59e0b"
            else:
                pred_label = "Khẩn cấp"
                status_class = "metric-emergency"
                status_text = "🔴 Nguy cơ Khẩn cấp (Rủi ro rất cao)"
                gauge_color = "#ef4444"
                
            # Create a Gauge Chart for risk representation
            # Anomaly scores range roughly from -0.5 (very anomalous) to 0.5 (normal)
            # Normalize to 0% - 100% risk rating for business presentation
            # Score near 0.2-0.5 is very normal -> 0% - 20% risk
            # Score near -0.1 to 0 is abnormal -> 80% - 100% risk
            # Formula mapping: Risk % = clamp( (0.25 - score) / 0.4 * 100, 0, 100 )
            risk_pct = max(0.0, min(100.0, ((0.25 - pred_score) / 0.4) * 100))
            
            # Layout the tester results inside Liquid Glass cards
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown(f"""
                <div class="glass-card">
                    <h3>Kết quả phân tích</h3>
                    <div style="font-size: 1.3rem; font-weight: 600; margin: 10px 0;" class="{status_class}">
                        {status_text}
                    </div>
                    <p><b>Điểm rủi ro (Score):</b> <code style="font-size: 1.1rem;">{pred_score:.5f}</code></p>
                    <p><b>Chỉ số rủi ro hệ thống:</b> <b>{risk_pct:.1f}%</b></p>
                    <div style="background-color: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; font-size: 0.9rem; color: #94a3b8;">
                        💡 <b>Nhận định:</b> Giao dịch với lượng tiền {'rất lớn' if test_amount > 1e8 else 'trung bình'} 
                        vào lúc {test_hour}h do {'nhân viên' if emp_val_int else 'khách hàng'} thực hiện. 
                        {'Giao dịch này hoàn toàn phù hợp với thói quen và quy luật thông thường.' if pred_label == 'Bình thường' else 'Giao dịch này đi chệch khỏi quy luật thông thường của dữ liệu lịch sử và cần được giám sát thêm.'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_res2:
                # Plotly gauge chart
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = risk_pct,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Chỉ số phần trăm rủi ro (%)", 'font': {'color': '#94a3b8', 'family': 'Outfit'}},
                    number = {'font': {'color': '#fff', 'family': 'Outfit'}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                        'bar': {'color': gauge_color},
                        'bgcolor': "rgba(255, 255, 255, 0.05)",
                        'borderwidth': 1,
                        'bordercolor': "rgba(255, 255, 255, 0.1)",
                        'steps': [
                            {'range': [0, 40], 'color': 'rgba(16, 185, 129, 0.1)'},
                            {'range': [40, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                            {'range': [75, 100], 'color': 'rgba(239, 68, 68, 0.1)'}
                        ]
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8', family='Outfit'),
                    height=300,
                    margin=dict(l=20, r=20, b=20, t=40)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
