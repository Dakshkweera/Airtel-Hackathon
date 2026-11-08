"""Bilingual text. Product names and prices are never translated; reasons and messages are."""

REFUSE = {
    "city": ("This product is not yet available in your city.", "यह प्रोडक्ट अभी आपके शहर में उपलब्ध नहीं है।"),
    "staff": ("This needs at least {n} staff.", "इसके लिए कम से कम {n} कर्मचारी चाहिए।"),
    "sites": ("This needs at least {n} branches.", "इसके लिए कम से कम {n} शाखाएँ चाहिए।"),
    "gst": ("This needs an active GST number.", "इसके लिए चालू GST नंबर ज़रूरी है।"),
    "gst_blocked": ("This needs an active GST number, and yours is cancelled or suspended.",
                    "इसके लिए चालू GST नंबर ज़रूरी है, और आपका GST रद्द या निलंबित है।"),
}
DEP_ADDED = ("This works only with an internet connection, so we added one.",
             "यह सिर्फ़ इंटरनेट कनेक्शन के साथ चलता है, इसलिए हमने एक जोड़ दिया।")
NO_DEP = ("This needs an internet connection and none is available in your city.",
          "इसके लिए इंटरनेट कनेक्शन चाहिए और आपके शहर में कोई उपलब्ध नहीं है।")

# one plain sentence per product, tied to the owner's answers
REASON = {
    "P01": ("Fastest line for heavy daily use at {staff} staff.", "{staff} लोगों के भारी रोज़ाना इस्तेमाल के लिए सबसे तेज़ लाइन।"),
    "P02": ("Fast, steady fibre for {staff} people to work online all day.", "{staff} लोगों के पूरे दिन ऑनलाइन काम के लिए तेज़, स्थिर फाइबर।"),
    "P03": ("A lighter fibre line that covers everyday billing and browsing.", "रोज़ के बिलिंग और ब्राउज़िंग के लिए हल्की फाइबर लाइन।"),
    "P04": ("Plug-and-play internet that can be live in about 2 days, no digging.", "प्लग-एंड-प्ले इंटरनेट, लगभग 2 दिन में चालू, कोई खुदाई नहीं।"),
    "P05": ("A dedicated line so machines and systems never share bandwidth.", "समर्पित लाइन ताकि मशीनें और सिस्टम बैंडविड्थ साझा न करें।"),
    "P06": ("A landline number for customers to reach you.", "ग्राहकों के लिए लैंडलाइन नंबर।"),
    "P07": ("A business mobile line so billing and UPI keep working.", "बिज़नेस मोबाइल लाइन ताकि बिलिंग और UPI चलते रहें।"),
    "P08": ("Connected SIMs for your machines and sensors.", "आपकी मशीनों और सेंसर के लिए कनेक्टेड SIM।"),
    "P09": ("Backup internet takes over if the main line drops, so work does not stop.", "मुख्य लाइन बंद हो तो बैकअप इंटरनेट चालू, काम नहीं रुकता।"),
    "P10": ("Links all {sites} branches on one secure network.", "सभी {sites} शाखाओं को एक सुरक्षित नेटवर्क पर जोड़ता है।"),
    "P11": ("Calls through the cloud, no extra phone hardware.", "क्लाउड से कॉल, अलग फ़ोन हार्डवेयर नहीं।"),
    "P12": ("Meet customers and staff on video without travel.", "बिना सफ़र के ग्राहकों और स्टाफ से वीडियो पर मिलें।"),
    "P13": ("A fixed address for CCTV or remote access.", "CCTV या रिमोट एक्सेस के लिए स्थिर पता।"),
    "P14": ("A managed router so you never have to set it up.", "मैनेज्ड राउटर, सेटअप की चिंता नहीं।"),
    "P15": ("Message customers on WhatsApp from one business number.", "एक बिज़नेस नंबर से ग्राहकों को WhatsApp पर संदेश भेजें।"),
    "P16": ("A professional email for each of your {qty} people.", "आपके {qty} लोगों में से हर एक के लिए प्रोफेशनल ईमेल।"),
    "P17": ("1 TB cloud copy of your files, safe from a dead laptop.", "आपकी फ़ाइलों की 1 TB क्लाउड कॉपी, लैपटॉप खराब होने पर भी सुरक्षित।"),
    "P18": ("A simple website and your own web address, so customers find you online.", "एक सरल वेबसाइट और आपका अपना वेब पता, ताकि ग्राहक आपको ऑनलाइन ढूँढ सकें।"),
    "P19": ("Billing and stock on your phone or counter.", "फ़ोन या काउंटर पर बिलिंग और स्टॉक।"),
    "P20": ("Virus and fraud protection for {qty} computers that hold your data.", "आपके डेटा वाले {qty} कंप्यूटरों के लिए वायरस और फ्रॉड सुरक्षा।"),
    "P21": ("Collects machine data on one gateway.", "मशीनों का डेटा एक गेटवे पर इकट्ठा करता है।"),
    "P22": ("Separate safe Wi-Fi for staff and for guests.", "स्टाफ और मेहमानों के लिए अलग सुरक्षित Wi-Fi।"),
    "P23": ("Watch your shop from your phone, day and night.", "अपनी दुकान फ़ोन से देखें, दिन-रात।"),
    "P24": ("A cloud phone line for each of your team.", "आपकी टीम में हर किसी के लिए क्लाउड फ़ोन लाइन।"),
    "P25": ("Keep accounts and GST filing in one place.", "हिसाब-किताब और GST फ़ाइलिंग एक जगह।"),
}

PLAN_NAMES = {
    "dukaan": ("Dukaan Starter", "दुकान स्टार्टर", "Online and connected for a small shop, no GST needed",
               "छोटी दुकान के लिए ऑनलाइन और कनेक्टेड, GST ज़रूरी नहीं"),
    "clinic": ("Clinic & Office Pro", "क्लिनिक और ऑफिस प्रो", "Reliable internet, email and security for your office",
               "आपके ऑफिस के लिए भरोसेमंद इंटरनेट, ईमेल और सुरक्षा"),
    "multi": ("Multi-Store Connect", "मल्टी-स्टोर कनेक्ट", "Every branch on one network, with CCTV",
              "हर शाखा एक नेटवर्क पर, CCTV के साथ"),
    "factory": ("Factory Connect", "फैक्ट्री कनेक्ट", "A dedicated line, machine connectivity and a team toolkit",
                "समर्पित लाइन, मशीन कनेक्टिविटी और टीम टूलकिट"),
    "mobile": ("Business Postpaid 299", "बिज़नेस पोस्टपेड 299", "Just a mobile plan, nothing extra",
               "सिर्फ़ मोबाइल प्लान, और कुछ नहीं"),
    "custom": ("Your plan", "आपका प्लान", "Built from what you asked for", "आपकी माँग के हिसाब से"),
}

BTYPE_LABEL = {
    "shop": ("shop", "दुकान"), "salon": ("salon or pharmacy", "सैलून या फार्मेसी"),
    "office": ("office or clinic", "ऑफिस या क्लिनिक"), "restaurant": ("restaurant or multi-store business", "रेस्टोरेंट या मल्टी-स्टोर बिज़नेस"),
    "factory": ("factory", "फैक्ट्री"), "mobile": ("mobile-only", "सिर्फ़ मोबाइल"),
}

# conversation lines: (en, hi)
T = {
    "greet": ("Namaste! 👋 I'm your Udyam Digital helper. I'll find the right plan in about 5 quick questions, or you can build your own and watch the price as you go. No visit needed. Speak or type in any language you like.\n\nWhat kind of business do you run?",
              "नमस्ते! 👋 मैं आपका Udyam Digital सहायक हूँ। सिर्फ़ 5 छोटे सवालों में सही प्लान ढूँढ दूँगा, या आप खुद अपना प्लान बनाकर भाव लाइव देख सकते हैं। किसी विज़िट की ज़रूरत नहीं। आप किसी भी भाषा में बोलें या लिखें।\n\nआप कौन-सा बिज़नेस चलाते हैं?"),
    "q_btype": ("What kind of business do you run?", "आप कौन-सा बिज़नेस चलाते हैं?"),
    "q_counts": ("How many people work with you, and how many shops or branches do you have?",
                 "आपके साथ कितने लोग काम करते हैं, और कितनी दुकानें या शाखाएँ हैं?"),
    "q_city": ("Which city is your business in?", "आपका बिज़नेस किस शहर में है?"),
    "q_gst": ("Do you have a GST number?", "क्या आपके पास GST नंबर है?"),
    "q_spend": ("What do you pay for internet and phone each month today? Skip if you prefer.",
                "आज इंटरनेट और फ़ोन पर हर महीने कितना खर्च करते हैं? चाहें तो छोड़ सकते हैं।"),
    "got_it": ("Got it.", "ठीक है।"),
    "reco": ("Here's what I recommend for your {btype}: **{plan}**. Each item has a reason, and you can switch extras on or off.",
             "आपके {btype} के लिए मेरा सुझाव: **{plan}**। हर आइटम की वजह दी है, और आप एक्स्ट्रा चालू-बंद कर सकते हैं।"),
    "reco_mobile": ("A mobile plan is all you need. Here it is, nothing extra.",
                    "आपको सिर्फ़ मोबाइल प्लान चाहिए। ये रहा, और कुछ नहीं।"),
    "dropped": ("I left out some items you can't take yet, and why is shown below.",
                "कुछ आइटम मैंने हटा दिए हैं जो अभी नहीं मिल सकते। वजह नीचे दी है।"),
    "handoff": ("This is a bigger setup, so a sales expert will follow up with this chat. You can still look at the indicative price above.",
                "यह बड़ा सेटअप है, इसलिए सेल्स विशेषज्ञ इस चैट के साथ आपसे संपर्क करेंगे। ऊपर का अनुमानित भाव आप देख सकते हैं।"),
    "handoff_ask": ("Sure, I've passed this chat to our sales team so they can follow up. You won't need to repeat anything.",
                    "ज़रूर, मैंने यह चैट हमारी सेल्स टीम को दे दी है। आपको कुछ दोहराना नहीं पड़ेगा।"),
    "wanted_head": ("About what you asked for:", "आपने जो माँगा उसके बारे में:"),
    "added_dep": ("{name} works only with an internet connection, so I added {dep}.",
                  "{name} सिर्फ़ इंटरनेट कनेक्शन के साथ चलता है, इसलिए मैंने {dep} जोड़ दिया।"),
    "refused_one": ("{name}: {reason}", "{name}: {reason}"),
    "offer_instead": ("Nearest option: {alt}.", "सबसे नज़दीकी विकल्प: {alt}।"),
    "mobile_only": ("Sure, just a mobile plan. Nothing else added.", "ठीक है, सिर्फ़ मोबाइल प्लान। और कुछ नहीं जोड़ा।"),
    "costly": ("I understand. You keep one bill, one helpline and backup internet, and billing and UPI keep working. I can't change prices, but here's a smaller option:",
               "समझता हूँ। आपको एक बिल, एक हेल्पलाइन और बैकअप इंटरनेट मिलता है, और बिलिंग व UPI चलते रहते हैं। मैं भाव नहीं बदल सकता, पर ये एक छोटा विकल्प है:"),
    "costly_min": ("This is already our smallest plan for you. You can switch off extras to bring it down.",
                   "यह आपके लिए हमारा सबसे छोटा प्लान है। एक्स्ट्रा बंद करके इसे और कम कर सकते हैं।"),
    "cheaper": ("I can't compare with other companies' prices. I can compare with what you pay today. Here's a smaller option if cost is the worry:",
                "मैं दूसरी कंपनियों के भाव से तुलना नहीं कर सकता। आज आप जो देते हैं उससे तुलना कर सकता हूँ। खर्च की चिंता है तो ये छोटा विकल्प है:"),
    "notneeded": ("No problem. Switch off anything you don't need in the list above. I only keep what you choose.",
                  "कोई बात नहीं। ऊपर की सूची में जो नहीं चाहिए उसे बंद कर दें। मैं वही रखूँगा जो आप चुनें।"),
    "think": ("Take your time. I've saved your quote. I can remind you tomorrow and in 3 days.",
              "आराम से सोचिए। मैंने आपका कोट सेव कर दिया है। मैं कल और 3 दिन बाद याद दिला सकता हूँ।"),
    "decline": ("Understood, I won't push. Your quote stays saved if you change your mind.",
                "समझ गया, मैं ज़ोर नहीं दूँगा। मन बदले तो आपका कोट सेव रहेगा।"),
    "reminder_set": ("Done. I'll remind you after 1 day and after 3 days. 👍", "हो गया। मैं 1 दिन और 3 दिन बाद याद दिलाऊँगा। 👍"),
    "go_papers": ("Great! Next is the paperwork. It takes a few minutes and uses only 4 documents.",
                  "बहुत बढ़िया! अब कागज़ी कार्रवाई। कुछ ही मिनट लगेंगे और सिर्फ़ 4 दस्तावेज़ चाहिए।"),
    "need_plan_first": ("Let me first find your plan. ", "पहले आपका प्लान ढूँढ लेता हूँ। "),
    "order_none": ("You don't have an order yet. Let's pick your plan first.", "अभी आपका कोई ऑर्डर नहीं है। पहले प्लान चुन लेते हैं।"),
    "order_status": ("Here's your order right now.", "ये रहा आपके ऑर्डर का अभी का हाल।"),
    "fallback_q": ("Sorry, I didn't catch that. ", "माफ़ कीजिए, मैं समझ नहीं पाया। "),
    "kyc_blocked_gst": ("Your GST registration is cancelled or suspended, so products that need GST were removed from your plan.",
                        "आपका GST रद्द या निलंबित है, इसलिए GST वाले प्रोडक्ट आपके प्लान से हटा दिए गए हैं।"),
    "order_placed": ("Your order is placed! 🎉 I'll update you at every step, so there's no need to call us.",
                     "आपका ऑर्डर हो गया! 🎉 हर कदम पर मैं आपको बताता रहूँगा, फ़ोन करने की ज़रूरत नहीं।"),
    "custom_intro": ("Let's build it together. Tell me what you need, tap a tile, or just type it. I'll keep the price updated as we go, and I'll never add anything you didn't ask for.",
                     "चलिए मिलकर बनाते हैं। बताइए क्या चाहिए, किसी टाइल पर टैप करें या टाइप करें। मैं भाव अपडेट करता रहूँगा, और जो आपने नहीं माँगा वो कभी नहीं जोड़ूँगा।"),
    "custom_empty": ("Nothing picked yet. Tap a tile or tell me what you need, for example “internet and CCTV”.",
                     "अभी कुछ नहीं चुना। किसी टाइल पर टैप करें या बताएँ, जैसे “इंटरनेट और CCTV”।"),
    "c_added": ("➕ **{name}** added. {reason} (+₹{price}/month{setup})", "➕ **{name}** जोड़ा। {reason} (+₹{price}/माह{setup})"),
    "c_setup": (", ₹{n} setup", ", ₹{n} सेटअप"),
    "c_qty": ("🔢 **{name}** is now ×{qty}.", "🔢 **{name}** अब ×{qty} है।"),
    "c_removed": ("➖ Removed **{name}**.", "➖ **{name}** हटाया।"),
    "c_total": ("Running total: **₹{m}/month** · ₹{s} one-time setup.", "अभी तक का कुल: **₹{m}/माह** · ₹{s} एक बार का सेटअप।"),
    "c_note_est": ("This is an estimate until I know your city, team size and GST.", "जब तक मुझे आपका शहर, टीम और GST पता नहीं, यह अनुमान है।"),
    "c_ask_pre": ("So I only show what you can buy: ", "ताकि मैं सिर्फ़ वही दिखाऊँ जो आप ले सकें: "),
    "c_removed_now": ("Now that I know more, I had to take out **{name}**: {reason}", "अब ज़्यादा जानकारी मिली, इसलिए **{name}** हटाना पड़ा: {reason}"),
    "c_suggest": ("Many people with this also take **{name}**. {reason} (+₹{price}/month). Want it? No pressure.",
                  "इसके साथ कई लोग **{name}** भी लेते हैं। {reason} (+₹{price}/माह)। चाहिए? कोई दबाव नहीं।"),
    "c_explain": ("**{name}**: {reason} It costs ₹{price}/month{setup}.", "**{name}**: {reason} इसकी कीमत ₹{price}/माह{setup} है।"),
    "c_done": ("Here's your plan, exactly what you picked. Change anything below.", "ये रहा आपका प्लान, ठीक वही जो आपने चुना। नीचे कुछ भी बदल सकते हैं।"),
    "c_pending": ("Needs a GST number, which I'll confirm.", "इसके लिए GST नंबर चाहिए, जो मैं पक्का करूँगा।"),
    "fallback_hint": ("You can tap an option, or just tell me in your own words, like “clinic in Indore, 6 staff, I have GST”.",
                      "आप किसी विकल्प पर टैप करें, या अपने शब्दों में बताएँ, जैसे “इंदौर में क्लिनिक, 6 स्टाफ, GST है”।"),
    "bt_guess": ("I'll treat that as a small shop or service for now. Tell me if it's an office or a factory.",
                 "मैं इसे अभी छोटी दुकान या सर्विस मान रहा हूँ। ऑफिस या फैक्ट्री हो तो बताइए।"),
    "price_of": ("**{name}**: ₹{price}/month{setup}. {reason}", "**{name}**: ₹{price}/माह{setup}। {reason}"),
    "fallback_plan": ("Sorry, I didn't catch that. You can say “continue” to start the paperwork, ask about any product, or tell me what to change.",
                      "माफ़ कीजिए, मैं समझ नहीं पाया। आप “आगे बढ़ो” कहकर कागज़ी कार्रवाई शुरू कर सकते हैं, किसी प्रोडक्ट के बारे में पूछ सकते हैं, या बदलाव बता सकते हैं।"),
    "kyc_where": ("I've opened the paperwork screen. On each document row, tap “📷 Photo” or “📎 PDF / file” to add it. No documents handy? Open “Try a sample applicant” at the top.",
                  "मैंने कागज़ात की स्क्रीन खोल दी है। हर दस्तावेज़ की पंक्ति में “📷 फ़ोटो” या “📎 PDF / फ़ाइल” दबाकर जोड़ें। दस्तावेज़ पास में नहीं हैं? ऊपर “सैंपल आवेदक आज़माएँ” खोलें।"),
    "recall_head": ("Here's what I remember so far:", "अब तक मुझे ये याद है:"),
    "recall_none": ("You haven't told me anything yet. What kind of business do you run?", "आपने अभी तक कुछ नहीं बताया। आप कौन-सा बिज़नेस चलाते हैं?"),
    "recall_plan": ("Your current plan: {plan} at ₹{price}/month.", "आपका मौजूदा प्लान: {plan}, ₹{price}/महीना।"),
    "stage_update": ("Update: {stage}.", "अपडेट: {stage}।"),
}

STAGES = [
    ("Papers checked", "कागज़ात जाँचे गए"),
    ("Setup fee received", "सेटअप शुल्क मिला"),
    ("Engineer booked", "इंजीनियर तय हुआ"),
    ("Installed", "इंस्टॉल हो गया"),
    ("Service started", "सर्विस शुरू"),
]

KYC_MSG = {
    "gst_format": ("This GST number looks wrong. Please check it.", "यह GST नंबर गलत लगता है। कृपया जाँचें।"),
    "gst_checksum": ("This GST number has a typing mistake.", "इस GST नंबर में टाइपिंग की गलती है।"),
    "gst_status": ("Your GST registration is cancelled or suspended, so some products are not available.",
                   "आपका GST रजिस्ट्रेशन रद्द या निलंबित है, इसलिए कुछ प्रोडक्ट उपलब्ध नहीं हैं।"),
    "gst_notfound": ("We could not find this GST number.", "हमें यह GST नंबर नहीं मिला।"),
    "udyam_notfound": ("We could not find this Udyam number.", "हमें यह Udyam नंबर नहीं मिला।"),
    "missing_gst_certificate": ("Please upload your GST certificate.", "कृपया अपना GST प्रमाणपत्र अपलोड करें।"),
    "missing_udyam_certificate": ("Please upload your Udyam certificate.", "कृपया अपना Udyam प्रमाणपत्र अपलोड करें।"),
    "missing_signatory_id": ("Please upload your ID.", "कृपया अपनी ID अपलोड करें।"),
    "missing_address_proof": ("Please upload a recent address proof.", "कृपया हाल का पता प्रमाण अपलोड करें।"),
    "names": ("The business name on your GST certificate and Udyam certificate do not match.",
              "आपके GST प्रमाणपत्र और Udyam प्रमाणपत्र पर बिज़नेस का नाम मेल नहीं खाता।"),
    "gst_on_cert": ("The GST number on the certificate is different from the one you typed.",
                    "प्रमाणपत्र पर GST नंबर आपके टाइप किए नंबर से अलग है।"),
    "address": ("The address on your bill is different from your GST address.", "आपके बिल का पता आपके GST पते से अलग है।"),
    "bill_old": ("Your bill is older than 3 months. Please upload a recent one.", "आपका बिल 3 महीने से पुराना है। कृपया हाल का बिल अपलोड करें।"),
    "id_expired": ("Your ID has expired. Please upload a valid one.", "आपकी ID की अवधि खत्म हो गई है। कृपया वैध ID अपलोड करें।"),
    "id_unreadable": ("We could not read the name on your ID. Please retake the photo.", "ID पर नाम पढ़ा नहीं जा सका। कृपया फ़ोटो दोबारा लें।"),
    "review": ("This photo was hard to read, so a reviewer will check it.", "यह फ़ोटो पढ़ने में मुश्किल थी, इसलिए एक रिव्यूअर इसे जाँचेगा।"),
    "ok": ("Looks good.", "सब ठीक है।"),
}


def t(key, lang, **kw):
    en, hi = T[key]
    s = hi if lang == "hi" else en
    return s.format(**kw) if kw else s


def pick(pair, lang, **kw):
    s = pair[1] if lang == "hi" else pair[0]
    return s.format(**kw) if kw else s
