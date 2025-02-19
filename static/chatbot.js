import { useState } from "react";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "\uD83D\uDC4B Hi! I’m your Virtual Assistant. How can I assist you today? Here are my services:\n\n✅ Web Presence Engineering\n✅ Web Design & Development\n✅ UI/UX Solutions\n✅ E-commerce Solutions\n✅ Mobile & Web-Based Apps\n✅ Digital Marketing (SEO, SMO, SMM)\n✅ IT Development & Services\n✅ Cyber Security Solutions\n\n📌 Just ask me anything!",
    },
  ]);

  const [input, setInput] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [userDetails, setUserDetails] = useState({ name: "", email: "", company: "" });

  const handleSendMessage = () => {
    if (!input.trim()) return;
    setMessages([...messages, { sender: "user", text: input }]);
    handleBotResponse(input);
    setInput("");
  };

  const handleBotResponse = (userInput) => {
    let response = "I’m not sure about that. Can you rephrase?";
    if (userInput.toLowerCase().includes("price")) {
      response = "Sure! You can check our Digital Marketing Packages here: \n🔗 [View Pricing](https://www.easylinkindia.com/digital-marketing-packages-india.php)";
    } else if (userInput.toLowerCase().includes("thank you")) {
      setShowForm(true);
      response = "Glad to assist you! 😊 Can I get your details to stay in touch?";
    }
    setMessages([...messages, { sender: "bot", text: response }]);
  };

  return (
    <div className="w-96 bg-gray-100 p-4 rounded-xl shadow-lg fixed bottom-4 right-4">
      <div className="h-64 overflow-y-auto mb-4 p-2 border border-gray-300 rounded-md bg-white">
        {messages.map((msg, index) => (
          <div key={index} className={msg.sender === "bot" ? "text-left" : "text-right"}>
            <p className={`p-2 my-1 rounded-md ${msg.sender === "bot" ? "bg-blue-200" : "bg-green-200"}`}>
              {msg.text}
            </p>
          </div>
        ))}
      </div>
      {showForm ? (
        <div className="space-y-2">
          <input
            type="text"
            placeholder="Your Name"
            className="w-full p-2 border rounded"
            onChange={(e) => setUserDetails({ ...userDetails, name: e.target.value })}
          />
          <input
            type="email"
            placeholder="Your Email"
            className="w-full p-2 border rounded"
            onChange={(e) => setUserDetails({ ...userDetails, email: e.target.value })}
          />
          <input
            type="text"
            placeholder="Company Name"
            className="w-full p-2 border rounded"
            onChange={(e) => setUserDetails({ ...userDetails, company: e.target.value })}
          />
          <button className="w-full bg-blue-500 text-white p-2 rounded" onClick={() => setShowForm(false)}>
            Submit
          </button>
        </div>
      ) : (
        <div className="flex gap-2">
          <input
            type="text"
            className="flex-1 p-2 border rounded"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button className="bg-blue-500 text-white p-2 rounded" onClick={handleSendMessage}>
            Send
          </button>
        </div>
      )}
    </div>
  );
}
