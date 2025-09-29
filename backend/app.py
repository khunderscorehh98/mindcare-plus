import subprocess
import gradio as gr

# Knowledge context for MindCare+
MINDCARE_CONTEXT = """
Perceived Challenges:
Mental health remains a critical yet often overlooked issue in Brunei. Despite growing global awareness, mental health stigma continues to discourage individuals from seeking professional help. Cultural and religious norms often frame distress as a personal weakness or spiritual impurity, resulting in silence and untreated conditions (Cambridge University Press, 2019).

Another major challenge lies in the limited availability of affordable mental health services. While private therapy sessions are available, their costs remain prohibitive for students, young professionals, and lower-income individuals. Public healthcare, despite being subsidized, is frequently overwhelmed by high demand and limited specialized resources (World Health Organization, 2017).

In addition, a lack of awareness and accurate data compounds the problem. Although reported cases of anxiety disorders increased from 1,515 in 2021 to 1,637 in 2022, experts believe the actual numbers are far higher due to stigma and underreporting (The Scoop, 2023). Suicide rates also rose from 1.9 per 100,000 in 2015 to 3.6 per 100,000 in 2018, although these figures are likely underestimated because of cultural taboos that discourage reporting (Cambridge University Press, 2019).

The country’s mental health infrastructure is limited, with only 1.7 psychiatrists and 4.8 psychologists per 100,000 people—barely sufficient to meet the growing demand (World Health Organization, 2017). In 2024 alone, over 13,000 individuals sought mental health treatment in Brunei, compared to around 11,200 in 2023, demonstrating a rapid rise in demand and placing further strain on an already stretched system (LinkedIn, 2024).

Students, young adults, and working professionals are particularly at risk. Research shows that 85% of healthcare workers experience burnout, 21% report depression or anxiety symptoms, and 2% have had suicidal thoughts within six months (The Scoop, 2023). This data reflects a broader national crisis that requires urgent intervention.

Offered Solutions:
MindCare+ is designed to address the growing mental health challenges in Brunei by providing an innovative, accessible, and culturally sensitive digital platform. The solution focuses on overcoming stigma, affordability issues, and gaps in mental health infrastructure through a combination of technology-driven tools and professional support.

The platform integrates AI-based mental health check-ins, enabling early detection of emotional distress through user-friendly assessments. This approach allows individuals to receive timely recommendations, reducing the likelihood of untreated conditions and lowering the burden on public health systems. In addition, virtual counseling sessions with licensed therapists provide private, affordable, and convenient access to professional care, removing the traditional barriers associated with in-person therapy (World Health Organization, 2017).

MindCare+ also emphasizes anonymity and confidentiality, which are critical for reducing stigma in culturally conservative environments such as Brunei (Cambridge University Press, 2019). By allowing users to seek help without fear of social judgment, the platform encourages more individuals to access mental health services.

Furthermore, the platform incorporates community support features such as peer discussion forums, live workshops, and mindfulness resources. These components not only foster a supportive environment but also promote mental health education, helping users develop coping skills and resilience (The Scoop, 2023). The combination of professional guidance and community engagement creates a holistic ecosystem for mental wellness.

Lastly, MindCare+ offers a freemium business model, where basic tools are provided for free while premium subscriptions unlock advanced features such as personalized therapy sessions and AI-driven wellness plans. This ensures affordability while maintaining financial sustainability through scalable revenue streams such as corporate wellness programs.

In essence, MindCare+ delivers an innovative and sustainable solution that improves mental health accessibility, reduces stigma, and supports Brunei’s broader efforts to enhance community well-being.
"""

def run_llama(prompt):
    full_prompt = f"""
You are MindCare+, an AI chatbot for mental health in Brunei. 
Use the following knowledge when answering questions. 
If a question is unrelated, politely redirect to mental health-related support.

Knowledge:
{MINDCARE_CONTEXT}

User: {prompt}
AI:
"""
    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=full_prompt,
        text=True,
        capture_output=True
    )
    return result.stdout.strip()

with gr.Blocks() as demo:
    gr.Markdown("MindCare+ AI ChatBot")

    chatbot = gr.Chatbot()
    msg = gr.Textbox()

    def respond(message, chat_history):
        bot_response = run_llama(message)
        chat_history.append((message, bot_response))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

demo.launch()