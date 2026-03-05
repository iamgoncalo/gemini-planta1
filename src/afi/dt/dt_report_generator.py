import os
from fpdf import FPDF
from datetime import datetime

class MVPReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.set_text_color(48, 209, 88) # Planta Green
        self.cell(0, 10, 'PLANTA SMART HOMES / HORSE CFT', border=False, align='L')
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'AFI v6.0', border=False, align='R', ln=True)
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Documento Confidencial | Page {self.page_no()}', align='C')

def generate_report():
    print("Generating official HORSE CFT 'Impacto Inicial v0.1' Report...")
    
    pdf = MVPReport()
    pdf.add_page()
    
    # Title
    pdf.set_font('helvetica', 'B', 18)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 15, 'MVP: Digital Twin Operacional (Impacto Inicial v0.1)', ln=True, align='C')
    pdf.set_font('helvetica', 'I', 11)
    pdf.cell(0, 10, f'Data de Geracao: {datetime.now().strftime("%Y-%m-%d")}', ln=True, align='C')
    pdf.ln(10)

    # 1. Executive Summary
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, '1. Resumo Executivo & Conclusao de Milestones', ln=True)
    pdf.set_font('helvetica', '', 11)
    summary = (
        "Este relatorio formaliza a entrega do Milestone 5 do MVP 'Digital Twin Operacional "
        "Industrial (HORSE) - Core OS / Planta OS'. A infraestrutura foi implementada com sucesso, "
        "incluindo a fusao edge (OpenClaw), o calculo autonomo do campo de Liberdade (F = P/D) "
        "e a integracao de inteligenica artificial conversacional (LBM / Claude)."
    )
    pdf.multi_cell(0, 6, summary)
    pdf.ln(5)

    # 2. Causal Anomaly Detection
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, '2. Deteccao de Anomalias (Atribuicao Causal)', ln=True)
    pdf.set_font('helvetica', '', 11)
    causal_text = (
        "O motor PlantaOS LBM separou com sucesso as matrizes de Percepcao (P) e Distorcao (D). "
        "Durante as simulacoes do CFT, o sistema provou capacidade para distinguir matematicamente "
        "entre uma falha de sensor (P_FAILURE) e um pico ambiental/ocupacao (D_FAILURE), "
        "ultrapassando as limitacoes de sistemas tradicionais de Machine Learning."
    )
    pdf.multi_cell(0, 6, causal_text)
    pdf.ln(5)

    # 3. Financial ROI
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, '3. Projeccao Financeira e Eficiencia (ROI)', ln=True)
    pdf.set_font('helvetica', '', 11)
    roi_text = (
        "Com base na telemetria de 2025 fornecida pela HORSE, a aplicacao do modelo de Swarm "
        "Optimization de PlantaOS projeta a seguinte rentabilidade sobre o CAPEX de instalacao:\n\n"
        " - Poupanca Bruta Anual: EUR 4,412.38\n"
        " - Cashflow Liquido Anual: EUR 3,912.38 (pos-subscricao)\n"
        " - Payback do Sistema: 3.8 anos\n"
        " - NPV a 10 anos (taxa 5%): EUR 15,210.37\n\n"
        "Nota: Estes valores refletem uma reducao projetada de 27.7% em custos de manutencao e perdas termicas."
    )
    pdf.multi_cell(0, 6, roi_text)
    pdf.ln(5)

    # 4. Digital Twin Heatmap
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, '4. Digital Twin: F-Field Spatial Heatmap', ln=True)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 6, "Visualizacao termografica estrutural das zonas de atrito (Alta Distorcao / Baixo F) no piso terreo do HORSE CFT. As zonas a vermelho indicam estrangulamentos na fluidez do espaco.")
    pdf.ln(5)
    
    image_path = "horse_cft_f_field.png"
    if os.path.exists(image_path):
        pdf.image(image_path, x=15, y=pdf.get_y(), w=180)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, "[Imagem horse_cft_f_field.png nao encontrada - Execute dt03_heatmap.py primeiro]", ln=True)
        pdf.set_text_color(0, 0, 0)

    # Output
    output_file = "HORSE_CFT_MVP_Impacto_Inicial_v0.1.pdf"
    pdf.output(output_file)
    print(f"Success! Official PDF report generated: {output_file}")

if __name__ == '__main__':
    generate_report()
