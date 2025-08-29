import os
from flask import Flask, render_template, request, flash
from google.genai import Client

app = Flask(__name__)
app.secret_key = "super-secret-key"  # 🔑 For session messages

# 🔑 Hardcode your API key for now
GEMINI_API_KEY = "AIzaSyDc_RMkPlBFVbQ2v8BWpHlTKZyN_0M7BYA"

# Initialize Gemini client
client = Client(api_key=GEMINI_API_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    source_text = ""
    error = None

    if request.method == "POST":
        source_text = request.form.get("source_text", "").strip()
        if not source_text:
            error = "⚠️ Please paste some text to summarize."
        else:
            try:
                # ✅ Stronger summarization instruction
                prompt = f"Summarize the following text in a clear, concise way (not a rewrite, but a shorter summary):\n\n{source_text}"

                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )

                summary = response.text.strip()

                # Handle edge case: model didn't summarize
                if not summary or len(summary) >= len(source_text):
                    error = "⚠️ The model couldn't summarize effectively. Try shorter input text."

            except Exception as e:
                # Map common errors to friendlier messages
                if "quota" in str(e).lower():
                    error = "🚫 API quota exceeded. Please try again later."
                elif "api_key" in str(e).lower():
                    error = "🔑 Invalid or missing API key."
                else:
                    error = f"❌ Error from Gemini API: {e}"

        if error:
            flash(error, "danger")

    return render_template("index.html", summary=summary, source_text=source_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
