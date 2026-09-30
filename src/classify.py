"""Rule-based intent classifier over customer_message (+ agent_notes as a second, independent signal).
Returns a fine-grained intent and a team that should own it per support-policy s6."""
import re

# (intent, owning_team, regex) - first match wins; order matters (specific -> generic)
RULES = [
 ("Duplicate payment",      "Billing",   r"double payment|two times|two entries|paid once, statement|card charged|double charge|charged twice|same amount twice|twice on the same day|duplicate (payment|txn|charge)|double charge"),
 ("Payment ok, no order",   "Billing",   r"upi shows success|paid via upi|no order confirma|bank says|no order id|i have no orders|site says i have no|failed (ord|order) after payment|payment debited|amount deducted without|debited, no order|no order was created|order not showing|page failed after i paid|nothing shows in my account|deducted (but|without)|debit(ed|de) but"),
 ("GST invoice",            "Billing",   r"gst|invoice|firm'?s? gstin|\bbill\b|blil"),
 ("Coupon / price",         "Billing",   r"coupon|promo|discount|20% off|full price|price drop|cheaper"),
 ("Cancellation",           "Frontline", r"cancel|by mistake|stop the shipment|change of mind|ordered this withou?t asking|please reverse"),
 ("Address change",         "Frontline", r"old flat|moved house|pincode|wrong address|change (my )?address|address update"),
 ("Refund delay",           "Returns Desk", r"refund delay|refund not credited|rfnd pending|refnd was promised|reefund was promised|refund was promised|refund (was promised|not received|hasn|nowhere)|where is the money for the return|amount is nowhere|money hasn'?t come back|still waiting for my refund"),
 ("Return pickup",          "Returns Desk", r"pkp not done|pickup not done|pikcup|reverse pickup pending|waiting for (your|yoru) courier|pickup|pick up|picked up"),
 ("Wrong / damaged item",   "Logistics", r"not what i paid for|got (white|black|blue|red)|not what i asked for|the box says|incorrect product|wrong variant|transit damage|damaged in transit|damaged|dent|crack|different (colour|color|thing)|wrong (item|variant)|got something else|completely different"),
 ("Delivery not received",  "Logistics", r"something to show up|where is my stuff|front door|box never came|doorstep|dlvry delayed|delivery delayed|shipment not rcvd|shipment not received|order not delivered|not (been )?delivered|not received|haven'?t received|nothing (in hand|at my door)|marked it delivered|out for delivery|stuck on shipped|package not|parcel|paid, confirmed, then nothing|has not moved|nobody in my house|order status"),
 ("Warranty / hardware fault","Escalations & Warranty", r"strap|touch screen|not responding|unresponsive display|touch|display|warranty|stopped working|dead|not (charging|turning on|switching on)|won'?t (turn|power)|rma|died"),
 ("Connectivity",           "Frontline", r"losing my phone|stutter|goes silent|wifi|wiif|router|bt dropouts|connection dropping|dropouts|pair|bluetooth|disconnect|connection (drops|keeps)|won'?t connect"),
 ("Charging / battery",     "Frontline", r"dies by lunch|battery|batter|charg(?!ed)|drain"),
 ("App / firmware",         "Frontline", r"\bapp\b|firmware|update|white screen|sync"),
 ("Audio quality",          "Frontline", r"one ear|cannot hear me|silent|side silent|calls|noise|static|crackl|distort|frying|volume|muffled|one side|no sound|bass|mic"),
 ("Pre-sales / how-to",     "Frontline", r"otp|login|pre-sales|compatibility query|product enquiry|work w/|work with|will this|compatible|work with|connect two|survive a shower|does my|can i connect|nokia|spec|login|password|otp|sign in|account"),
]
COMPILED = [(i, t, re.compile(rx, re.I)) for i, t, rx in RULES]

def norm(s):
    s = str(s).lower().replace("\n", " ")
    return re.sub(r"\s+", " ", s)

def classify_text(msg):
    m = norm(msg)
    for intent, team, rx in COMPILED:
        if rx.search(m):
            return intent, team
    return "Unclassified", "Frontline"

def classify_row(msg, notes=""):
    """Message first; if unclassified fall back to agent note."""
    i, t = classify_text(msg)
    src = "message"
    if i == "Unclassified":
        i, t = classify_text(notes); src = "notes"
        if i == "Unclassified": src = "none"
    return i, t, src
