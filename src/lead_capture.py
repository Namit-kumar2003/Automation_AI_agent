import csv
import os
from datetime import datetime
from typing import Dict, Optional
from src.utils import validate_email, ensure_data_directory


def mock_lead_capture(name: str, email: str, platform: str):
    """
    Mock API function for lead capture (as required by assignment)
    
    Args:
        name: User's name
        email: User's email
        platform: Creator platform (YouTube, Instagram, TikTok, etc.)
    """
    print(f"\n{'=' * 60}")
    print(f"🎉 Lead captured successfully!")
    print(f"{'=' * 60}")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Creator Platform: {platform}")
    print(f"{'=' * 60}\n")


class LeadCapture:
    """Handles lead capture workflow"""
    
    def __init__(self):
        """Initialize lead capture system"""
        ensure_data_directory()
        self.leads_file = "data/leads.csv"
        self.current_lead = {}
    
    def collect_information(self) -> Optional[Dict]:
        """
        Collect all required lead information interactively
        Only calls mock API after collecting ALL three values
        
        Returns:
            Dictionary with lead data or None if collection failed
        """
        print("\n✨ Great! Let me collect a few details to get you started:\n")
        
        # Step 1: Collect name
        name = self._collect_name()
        if not name:
            return None
        
        # Step 2: Collect email
        email = self._collect_email()
        if not email:
            return None
        
        # Step 3: Collect creator platform
        platform = self._collect_platform()
        if not platform:
            return None
        
        # All three values collected - now call mock API
        lead_data = {
            "name": name,
            "email": email,
            "platform": platform
        }
        
        # Call mock API function (as required by assignment)
        mock_lead_capture(name, email, platform)
        
        # Save to CSV
        self._save_to_csv(lead_data)
        
        return lead_data
    
    def _collect_name(self) -> Optional[str]:
        """Collect and validate name"""
        while True:
            try:
                name = input("Your name: ").strip()
                if not name:
                    print("  ⚠️  Name is required. Please enter your name.")
                    continue
                return name
            except (KeyboardInterrupt, EOFError):
                print("\n  ❌ Lead capture cancelled.")
                return None
    
    def _collect_email(self) -> Optional[str]:
        """Collect and validate email"""
        while True:
            try:
                email = input("Your email: ").strip()
                if not email:
                    print("  ⚠️  Email is required. Please enter your email.")
                    continue
                if not validate_email(email):
                    print("  ⚠️  Please enter a valid email address (e.g., user@example.com)")
                    continue
                return email
            except (KeyboardInterrupt, EOFError):
                print("\n  ❌ Lead capture cancelled.")
                return None
    
    def _collect_platform(self) -> Optional[str]:
        """Collect creator platform"""
        print("\nWhich platform do you create content for?")
        print("(e.g., YouTube, Instagram, TikTok, Facebook, Twitch, etc.)")
        
        while True:
            try:
                platform = input("Creator Platform: ").strip()
                if not platform:
                    print("  ⚠️  Platform is required. Please specify your platform.")
                    continue
                return platform
            except (KeyboardInterrupt, EOFError):
                print("\n  ❌ Lead capture cancelled.")
                return None
    
    def _save_to_csv(self, lead_data: Dict):
        """Save lead to CSV file"""
        # Add timestamp
        lead_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        file_exists = os.path.isfile(self.leads_file)
        
        with open(self.leads_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "name", "email", "platform"])
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(lead_data)
        
        print(f"💾 Lead saved to {self.leads_file}")
    
    def view_all_leads(self):
        """Display all captured leads"""
        if not os.path.isfile(self.leads_file):
            print("\n📋 No leads captured yet.")
            return
        
        print("\n" + "=" * 80)
        print("CAPTURED LEADS - AUTOSTREAM")
        print("=" * 80)
        
        with open(self.leads_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            leads = list(reader)
            
            if not leads:
                print("No leads captured yet.")
                return
            
            for i, lead in enumerate(leads, 1):
                print(f"\nLead #{i}")
                print(f"  Timestamp: {lead['timestamp']}")
                print(f"  Name: {lead['name']}")
                print(f"  Email: {lead['email']}")
                print(f"  Platform: {lead['platform']}")
        
        print("\n" + "=" * 80)