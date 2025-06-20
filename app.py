import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 ColofFour LLC 在仓+在途库存合并工具", layout="centered")
st.title("📦 ColofFour LLC  在仓 + 在途 库存合并工具")
st.caption("上传你的在仓库存和在途库存，我将为你自动生成整合结果～")

# 上传文件
on_hand_file = st.file_uploader("📥 上传在仓库存文件（如：产品库存💲_产品库存）", type="csv", key="on_hand")
in_transit_file = st.file_uploader("📥 上传在途库存文件（如：A链订购总表_在途库存）", type="csv", key="in_transit")

if on_hand_file and in_transit_file:
    on_hand_df = pd.read_csv(on_hand_file)
    in_transit_df = pd.read_csv(in_transit_file)

    # 清洗在仓数据
    on_hand_cleaned = on_hand_df[['产品名称', 'SKU编码', '06/18']].dropna()
    on_hand_cleaned.columns = ['Name', 'SKU', 'In_stock']

    # 清洗在途数据（按 SKU 拆解）
    in_transit_long = []
    for idx, row in in_transit_df.iterrows():
        base_name = row['英文名称']
        for size in ['S', 'M', 'L']:
            sku = None
            if base_name and isinstance(base_name, str):
                name_parts = base_name.split()
                code_part = ''.join([word[0] for word in name_parts[:2]]).upper()
                sku = f"NP{code_part}001-{size}"
            qty = row[f'{size}数量']
            in_transit_long.append({'Name': base_name, 'SKU': sku, 'On_the_way': qty})

    in_transit_df_flat = pd.DataFrame(in_transit_long)

    # 合并
    combined_df = pd.merge(on_hand_cleaned, in_transit_df_flat, on='SKU', how='outer')
    combined_df['Name_x'] = combined_df['Name_x'].fillna(combined_df['Name_y'])
    combined_df = combined_df.rename(columns={'Name_x': 'Name'})
    combined_df = combined_df[['Name', 'SKU', 'In_stock', 'On_the_way']]
    combined_df = combined_df.fillna(0)
    combined_df['In_stock'] = combined_df['In_stock'].astype(int)
    combined_df['On_the_way'] = combined_df['On_the_way'].astype(int)

    st.success("✅ 合并完成！请在下方查看：")
    st.dataframe(combined_df)

    # 下载按钮
    csv = combined_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📤 下载合并后的CSV", csv, "combined_inventory.csv", "text/csv")

else:
    st.warning("请上传两个CSV文件以开始处理～")
