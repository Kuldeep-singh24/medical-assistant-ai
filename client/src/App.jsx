import { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const [file, setFile] = useState(null);
  const [uploadMsg, setUploadMsg] = useState("");

  const chatEndRef = useRef(null);

  useEffect(() => {

    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages]);

  // Upload PDF
  const uploadPDF = async () => {

    if (!file) {

      alert("Please select a PDF");
      return;

    }

    const formData = new FormData();

    formData.append("files", file);

    try {

      const response = await fetch(
        "https://medical-assistant-ai-7cp9.onrender.com/upload_pdfs/",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      setUploadMsg(data.messages);

      setSources((prev) => [
        ...new Set([...prev, file.name]),
      ]);

    } catch (error) {

      console.log(error);

      setUploadMsg("Upload failed");

    }

  };

  // Ask Question
  const askQuestion = async () => {

    if (!question.trim()) return;

    const userMessage = {
      type: "user",
      text: question,
    };

    setMessages((prev) => [...prev, userMessage]);

    setLoading(true);

    const formData = new FormData();

    formData.append("question", question);

    try {

      const response = await fetch(
        "https://medical-assistant-ai-7cp9.onrender.com/ask/",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      const botMessage = {
        type: "bot",
        text: data.response,
      };

      setMessages((prev) => [...prev, botMessage]);

      if (data.sources) {

        setSources([
          ...new Set(
            data.sources.map((src) =>
              src.split("\\").pop()
            )
          ),
        ]);

      }

    } catch (error) {

      console.log(error);

    }

    setQuestion("");
    setLoading(false);

  };

  return (

    <div className="app">

      {/* Sidebar */}
      <div className="sidebar">

        <div className="logo-section">

          <h2>🩺 Medical PDFs</h2>

          <p>
            Upload documents for AI analysis
          </p>

        </div>

        {/* Upload Card */}
        <div className="upload-card">

          <input
            type="file"
            onChange={(e) =>
              setFile(e.target.files[0])
            }
          />

          <button onClick={uploadPDF}>
            Upload PDF
          </button>

          {uploadMsg && (
            <div className="upload-success">
              {uploadMsg}
            </div>
          )}

        </div>

        {/* Sources */}
        <div className="source-section">

          <h3>📄 Sources</h3>

          {sources.length > 0 ? (

            <ul>

              {sources.map((source, index) => (

                <li key={index}>
                  {source}
                </li>

              ))}

            </ul>

          ) : (

            <p>No sources available</p>

          )}

        </div>

      </div>

      {/* Main Chat */}
      <div className="chat-container">

        {/* Header */}
        <div className="header">

          <h1>
            🩺 Medical Assistant Chatbot
          </h1>

          <p>
            AI Powered Medical Research Assistant
          </p>

        </div>

        {/* Chat Box */}
        <div className="chat-box">

          {messages.length === 0 && (

            <div className="empty-chat">

              <div className="empty-chat-content">

                <h2>
                  🩺 Welcome to Medical Assistant AI
                </h2>

                <p>
                  Upload medical PDFs and ask
                  AI-powered health questions.
                </p>

              </div>

            </div>

          )}

          {messages.map((msg, index) => (

            <div
              key={index}
              className={`message ${msg.type}`}
            >

              {msg.text}

            </div>

          ))}

          {loading && (

            <div className="typing">
              AI is typing...
            </div>

          )}

          <div ref={chatEndRef}></div>

        </div>

        {/* Input Box */}
        <div className="input-box">

          <input
            type="text"
            placeholder="Type your medical question..."
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            onKeyDown={(e) => {

              if (e.key === "Enter") {

                askQuestion();

              }

            }}
          />

          <button onClick={askQuestion}>
            Send
          </button>

        </div>

      </div>

    </div>

  );

}

export default App;