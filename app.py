import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Set up our Streamlit app
st.set_page_config(page_title="🛠️ Testing Report Analyzer", layout='wide')
st.title("🛠️ Testing Report Analyzer")
st.write("Analyze your testing reports with data cleaning, filtering, and visualization!")

# File uploader (CSV/Excel)
uploaded_files = st.file_uploader("Upload Testing Reports (CSV or Excel):", type=["csv","xlsx"],
accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file based on extension
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display basic file details
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024} KB")

        # Show first few rows of the DataFrame
        st.write("Preview the Head of the DataFrame")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing Values Filled!")

        # Test Status Summary (Pass/Fail Analysis)
        if "Status" in df.columns:
            st.subheader("📊 Test Case Status Summary")
            status_counts = df["Status"].value_counts()
            st.bar_chart(status_counts)  # Show bar chart of Pass/Fail status
            
            if st.checkbox(f"Show Pie Chart for {file.name}"):
                st.write("📌 Pass/Fail Distribution")
                st.write(status_counts.plot.pie(autopct="%1.1f%%"))

        # Security Level Filtering (if column exists)
        if "Security Level" in df.columns:
            st.subheader("🔍 Filter by Security Level")
            selected_levels = st.multiselect("Select Security Levels", df["Security Level"].unique())
            if selected_levels:
                df = df[df["Security Level"].isin(selected_levels)]
                st.write(f"Filtered Data (Showing {len(df)} rows)")

        # Column Selection for Conversion
        st.subheader("📌 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]  # Keep only selected columns

        # File Conversion Options
        st.subheader("🔃 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                buffer.seek(0)

            # Provide Download Button
            st.download_button(
                label=f"🔽 Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("✅ All Testing Reports Processed!")
