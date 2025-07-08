import os
import csv
import logging
import pandas as pd
from dotenv import load_dotenv
from together import Together  # type: ignore

from email_verifier import verify_email_neverbounce
from website_checker import extract_text_from_url, classify_website
from title_scorer import get_title_score_llm
from lead_ranker import calculate_lead_score

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API key from .env
load_dotenv()
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def process_leads_from_csv(input_file: str, output_file: str, target_role: str):
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames + [
            "email_status", "website_status", "title_score", "lead_score"
        ]  # type: ignore
        rows = []

        for row in reader:
            email = row.get("email", "").strip()
            website = row.get("domain", "").strip()
            title = row.get("title", "").strip()

            logging.info(f"🔍 Processing: {email} | {website} | {title}")

            # 1. Email verification
            email_data = verify_email_neverbounce(email)
            email_status = email_data["email_status"]

            # 2. Website classification
            full_url = f"https://{website}" if website and not website.startswith("http") else website
            site_content = extract_text_from_url(full_url)

            if site_content:
                website_status = classify_website(site_content)
            else:
                website_status = "unreachable"  # New fallback

            # 3. Title scoring
            title_score = get_title_score_llm(title, target_role)

            # 4. Lead score (final)
            lead_score = calculate_lead_score(
                title_score=title_score,
                email_status=email_status,
                website_status=website_status
            )

            row.update({
                "email_status": email_status,
                "website_status": website_status,
                "title_score": title_score,
                "lead_score": lead_score
            })

            rows.append(row)

    # Save full enriched output
    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logging.info(f"✅ Enriched leads saved to: {output_file}")

    # Create clean + sorted version
    try:
        df = pd.read_csv(output_file)
        clean_df = df[["name", "title", "email_status", "website_status", "lead_score"]]
        clean_df = clean_df.sort_values(by="lead_score", ascending=False)
        clean_df.to_csv("leads_clean_sorted.csv", index=False)
        logging.info("✅ Cleaned and sorted output saved to: leads_clean_sorted.csv")

        # 📊 Summary metrics
        total = len(df)
        valid_emails = df["email_status"].value_counts().get("valid", 0)
        real_sites = df["website_status"].value_counts().get("real_business", 0)
        avg_score = df["lead_score"].mean()
        logging.info("\n📊 Summary:")
        logging.info(f"• Total leads processed: {total}")
        logging.info(f"• Valid emails: {valid_emails}")
        logging.info(f"• Real business websites: {real_sites}")
        logging.info(f"• Average lead score: {round(avg_score, 2)}")

    except Exception as e:
        logging.error(f"❌ Failed to create cleaned output: {e}")

if __name__ == "__main__":
    input_csv = "leads_input.csv"
    output_csv = "leads_output.csv"
    target_role = input("🎯 Enter the target role to evaluate leads (e.g. 'Marketing Manager'): ").strip()
    process_leads_from_csv(input_csv, output_csv, target_role)