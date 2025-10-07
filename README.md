# 🧘‍♂️ Slowdown – Your Witty AI Wellness Companion

**Slowdown** is an AI Agent built with **OpenAI AgentKit (Agent Builder + SDK)**.  
It’s a friendly, witty digital companion that helps you pace your day, take breaks, and recharge — without nagging.  
Originally designed and trained in the OpenAI Agent Builder, this repository hosts its Python SDK integration code.

---

## 🌟 Features

- 💬 **Conversational wellness assistant** built with GPT-5  
- 🧠 **Short-term memory** (retains context within sessions)  
- ⚙️ **Integrated Guardrails** for PII and safe conversations  
- 📄 **Optional File Search** to pull tips or quotes from your custom text file  
- ✅ **User Approval Flow** before any proactive reminders  
- 🧩 **Exported Agent SDK** for local or backend integration

---

## 🧱 Project Structure

slowdown-agent/
│
├── slowdown_agent.py # Python SDK code generated from OpenAI Agent Builder
├── README.md # Project documentation (this file)


## 🧩 Customization

You can modify the Agent ID inside slowdown_agent.py to point to any Agent you’ve created in your OpenAI workspace.
To change your agent’s behavior:

Go to your OpenAI Agent Dashboard
Edit the “Slowdown” Agent’s Instructions or add new tools (Guard Rails, File Search, etc.)
Re-publish, then update your local SDK snippet if the agent ID changes.

## 🧠 Extending Slowdown

Future ideas for enhancement:

Integrate Google Calendar or Microsoft Outlook via MCP connector to schedule real break reminders.

Add voice interaction (Speech-to-Text + Text-to-Speech APIs).

Store daily reflection logs in a secure local or cloud database.

## 🤝 Contributing

Contributions, bug fixes, and improvements are welcome.

Feel free to fork this repo, submit a pull request, or open an issue.
