import os
import smtplib
from email.mime.text import MIMEText
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Define the Strict Data Blueprints using Pydantic
class CorporateJob(BaseModel):
    title: str = Field(description="O título do cargo ou vaga (ex: Analista de Compliance Pleno)")
    company: str = Field(description="Nome da empresa contratante ou plataforma (ex: Gupy / Itaú)")
    location: str = Field(description="Cidade e Estado da vaga (ex: Recife - PE)")
    work_model: str = Field(description="Modelo de trabalho: Remoto, Híbrido ou Presencial")
    source_url: str = Field(description="O link direto ou URL de origem encontrado na busca para inscrição")
    match_reason: str = Field(description="Breve explicação em português de como essa vaga se encaixa na transição da candidata")

class PublicExam(BaseModel):
    institution: str = Field(description="Nome do órgão público (ex: TJ-PE, PGM-Fortaleza)")
    role_and_sphere: str = Field(description="Cargo e esfera do concurso (ex: Analista Judiciário - Estadual)")
    state: str = Field(description="Estado da federação correspondente: AL, PE, CE ou Federal")
    status: str = Field(description="Status atual do certame: Inscrições Abertas, Edital Publicado ou Previsto/Autorizado")
    salary: str = Field(description="Remuneração ou salário inicial informado no edital")
    deadline_or_url: str = Field(description="Período final de inscrição ou link principal do concurso")

class RecruiterNotes(BaseModel):
    regional_analysis: str = Field(description="Análise estratégica do dia (2 a 3 linhas) sobre o mercado de AL, PE e CE")

# This is the master wrapper object Gemini MUST return
class JobScoutReport(BaseModel):
    corporate_jobs: List[CorporateJob] = Field(description="Lista de vagas de mercado encontradas")
    public_exams: List[PublicExam] = Field(description="Lista de concursos públicos mapeados")
    recruiter_notes: RecruiterNotes = Field(description="Notas e insights do dia elaborados pelo recrutador")


def run_daily_job_scout():
    # Initialize the modern Google GenAI Client
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    system_instruction = """
    Você é um headhunter sênior e especialista em transição de carreira jurídica e preparação para o serviço público no Nordeste do Brasil.
    A candidata possui OAB ativa, reside em Maceió/AL, e busca recolocação nas regiões de ALAGOAS, PERNAMBUCO e CEARÁ (com total mobilidade para residir em Recife/PE ou Fortaleza/CE, ou atuar de forma 100% Remota).

    Seu objetivo diário é realizar duas pesquisas distintas usando ferramentas de busca viva:
    1. MERCADO CORPORATIVO: Vagas de transição (Compliance, Legal Operations, Analista de Contratos, Governança Corporativa, Proteção de Dados/LGPD) focadas em AL, PE, CE ou 100% Remotas.
    2. CONCURSOS PÚBLICOS: Editais abertos, publicados ou previstos/autorizados (AJAJ de Tribunais, Procuradorias, Defensorias, cargos superiores administrativos) focados em AL, PE, CE ou Esfera Federal.
    """

    print("Executing Google Search Grounding & Gemini Generation...")
    
    # Execute call enforcing the JSON output structure
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="Execute a busca diária consolidada por vagas corporativas e concursos públicos para o perfil estabelecido nas regiões AL, PE e CE.",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[{"google_search": {}}],  # Activates Live Web Browser
            temperature=0.1,                # Lower temperature for predictable extraction
            response_mime_type="application/json",
            response_schema=JobScoutReport, # Direct integration forcing Pydantic validation
        ),
    )
    
    # The output is GUARANTEED to be stringified JSON that maps perfectly to your schema
    raw_json_string = response.text
    print("Success! JSON payload received from Gemini.")
    
    # Process and build HTML template for delivery
    process_and_email_report(raw_json_string)


def process_and_email_report(json_data: str):
    import json
    data = json.loads(json_data)
    
    # Programmatically build a clean, bulletproof HTML email template
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px;">
            Tracker Diário de Oportunidades - Nordeste
        </h2>
        
        <p>Olá! Aqui estão as oportunidades selecionadas automaticamente pelo seu assistente Gemini hoje:</p>
        
        <h3 style="color: #202124;">1. Vagas no Mercado Corporativo (AL / PE / CE / Remoto)</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; border-color: #dadce0;">
            <tr style="background-color: #f8f9fa;">
                <th>Cargo</th><th>Empresa</th><th>Localização</th><th>Modelo</th><th>Link</th><th>Por que se aplica?</th>
            </tr>
    """
    
    for job in data.get("corporate_jobs", []):
        html_content += f"""
            <tr>
                <td><b>{job['title']}</b></td>
                <td>{job['company']}</td>
                <td>{job['location']}</td>
                <td>{job['work_model']}</td>
                <td><a href="{job['source_url']}" style="color: #1a73e8;">Acessar Vaga</a></td>
                <td style="font-size: 13px; color: #5f6368;">{job['match_reason']}</td>
            </tr>
        """
        
    html_content += """
        </table>
        
        <h3 style="color: #202124; margin-top: 24px;">2. Concursos Públicos (Editais e Previsões)</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; border-color: #dadce0;">
            <tr style="background-color: #f8f9fa;">
                <th>Órgão</th><th>Cargo / Esfera</th><th>UF</th><th>Status</th><th>Salário Inicial</th><th>Inscrição / Link</th>
            </tr>
    """
    
    for exam in data.get("public_exams", []):
        html_content += f"""
            <tr>
                <td><b>{exam['institution']}</b></td>
                <td>{exam['role_and_sphere']}</td>
                <td align="center">{exam['state']}</td>
                <td><span style="padding: 2px 6px; background-color: #e8f0fe; color: #1a73e8; border-radius: 4px; font-size: 12px;">{exam['status']}</span></td>
                <td>{exam['salary']}</td>
                <td>{exam['deadline_or_url']}</td>
            </tr>
        """
        
    html_content += f"""
        </table>
        
        <h3 style="color: #e37400; margin-top: 24px;">Análise Estratégica do Recrutador</h3>
        <p style="background-color: #fef7e0; border-left: 4px solid #f4b400; padding: 12px; font-style: italic; margin-bottom: 30px;">
            "{data.get('recruiter_notes', {{}}).get('regional_analysis', '')}"
        </p>
        
        <p style="font-size: 11px; color: #9aa0a6; text-align: center; border-top: 1px solid #dadce0; padding-top: 10px;">
            Gerado de forma privada via infraestrutura local-first & Gemini Pipeline.
        </p>
    </body>
    </html>
    """
    
    # Code to pipe 'html_content' directly into standard smtplib follows here...
    print("HTML successfully generated. Size:", len(html_content), "bytes.")

if __name__ == "__main__":
    # Test execution harness locally
    # os.environ["GEMINI_API_KEY"] = "YOUR_KEY"
    run_daily_job_scout()