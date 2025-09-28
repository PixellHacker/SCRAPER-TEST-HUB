import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from datetime import datetime
import re
import urllib.parse
import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class VideoInfo:
    title: str
    url: str
    channel: str
    views: str
    upload_time: str
    duration: str
    thumbnail: str
    description: str

class YouTubeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
        
        # Ocean hazards in English
        self.hazards_english = [
            "tsunami", "cyclone", "storm surge", "high waves",
            "coastal erosion", "oil spill"
        ]
        
        # Ocean hazards in Hindi (focusing only on English and Hindi as requested)
        self.hazards_hindi = ["सुनामी", "चक्रवात", "तूफान", "ऊंची लहरें", "तटीय कटाव", "तेल रिसाव"]
        
        # Indian coastal states and cities for filtering
        self.indian_coastal_keywords = [
            # States
            "india", "भारत", "indian", "भारतीय",
            # Coastal States
            "gujarat", "गुजरात", "maharashtra", "महाराष्ट्र", "goa", "गोवा",
            "karnataka", "कर्नाटक", "kerala", "केरल", "tamil nadu", "तमिल नाडु",
            "andhra pradesh", "आंध्र प्रदेश", "telangana", "तेलंगाना", 
            "odisha", "ओडिशा", "west bengal", "पश्चिम बंगाल",
            # Major Coastal Cities
            "mumbai", "मुंबई", "chennai", "चेन्नई", "kochi", "कोच्चि", "cochin",
            "visakhapatnam", "विशाखापत्तनम", "kolkata", "कोलकाता", "calcutta",
            "surat", "सूरत", "vadodara", "वडोदरा", "rajkot", "राजकोट",
            "ahmedabad", "अहमदाबाद", "pune", "पुणे", "panaji", "पणजी",
            "mangalore", "मंगलौर", "udupi", "उडुपी", "thiruvananthapuram", "तिरुवनंतपुरम",
            "kozhikode", "कोझीकोड", "calicut", "कालीकट", "puducherry", "पुडुचेरी",
            "pondicherry", "पांडिचेरी", "tuticorin", "तूतीकोरिन", "madurai", "मदुराई",
            "coimbatore", "कोयंबटूर", "salem", "सलेम", "vellore", "वेल्लोर",
            "tirunelveli", "तिरुनेलवेली", "nellore", "नेल्लोर", "guntur", "गुंटूर",
            "vijayawada", "विजयवाड़ा", "kakinada", "काकीनाडा", "rajahmundry", "राजमुंद्री",
            "cuttack", "कटक", "bhubaneswar", "भुवनेश्वर", "puri", "पुरी",
            "balasore", "बालासोर", "paradip", "पारादीप", "haldia", "हल्दिया",
            "digha", "दीघा", "daman", "दमन", "diu", "दीव", "silvassa", "सिलवासा",
            # Coastal regions and features
            "arabian sea", "अरब सागर", "bay of bengal", "बंगाल की खाड़ी",
            "indian ocean", "हिंद महासागर", "malabar coast", "मालाबार तट",
            "coromandel coast", "कोरोमंडल तट", "konkan coast", "कोंकण तट",
            "coastal", "तटीय", "sea", "समुद्र", "ocean", "महासागर",
            # Weather systems affecting India
            "monsoon", "मानसून", "southwest monsoon", "दक्षिणपश्चिम मानसून",
            "northeast monsoon", "उत्तरपूर्व मानसून", "imd", "भारतीय मौसम विभाग",
            "cyclone warning", "चक्रवात चेतावनी", "ndma", "राष्ट्रीय आपदा प्रबंधन प्राधिकरण"
        ]
        
        # News channels and educational content to exclude
        self.exclude_channels = [
            # Major Indian News Channels
            "zee news", "aaj tak", "ndtv", "india today", "times now", "republic",
            "cnn news18", "news18", "abp news", "dd news", "ani", "pti",
            # Regional News Channels
            "tv9", "eenadu", "sakshi", "v6 news", "hmtv", "ntv", "manorama news",
            "asianet news", "mathrubhumi news", "kairali news", "janam tv",
            "puthiya thalaimurai", "polimer news", "news7 tamil", "thanthi tv",
            "sun news", "vijay news", "zee tamil", "news18 tamil nadu",
            # English News/Educational
            "bbc", "cnn", "discovery", "national geographic", "history channel",
            "documentary", "explained", "educational", "informative",
            # Government/Official Channels
            "doordarshan", "pib india", "ministry", "government", "official"
        ]
        
        # Keywords that indicate informational/educational content (to exclude)
        self.exclude_content_keywords = [
            # Educational/Informational
            "why", "how", "what is", "explained", "documentary", "facts about",
            "history of", "science behind", "causes of", "formation of",
            "education", "learning", "tutorial", "guide", "information",
            "knowledge", "study", "research", "analysis", "explainer",
            # Tourism/Infrastructure
            "tourist", "tourism", "visit", "travel", "bridge", "construction",
            "infrastructure", "development", "project", "plan", "proposal",
            "glass bridge", "sea bridge", "places to visit", "attractions",
            # General informative terms
            "first", "biggest", "largest", "amazing", "incredible", "facts",
            "top 10", "top 5", "list of", "compilation", "collection"
        ]
        
        # Keywords for emergency/distress content (to include)
        self.emergency_keywords = [
            # Emergency situations
            "help", "emergency", "rescue", "trapped", "stuck", "flood", "flooding",
            "water rising", "evacuate", "evacuation", "shelter", "relief",
            "disaster", "damage", "destroyed", "affected", "victims",
            # Live/Real-time content
            "live", "now", "happening now", "current", "ongoing", "breaking",
            "alert", "warning", "urgent", "immediate", "real time",
            # Distress calls in Hindi
            "मदद", "बचाओ", "आपातकाल", "बाढ़", "तूफान आ रहा है", "खतरा", "चेतावनी",
            "तत्काल", "अभी", "लाइव", "मौजूदा", "राहत", "नुकसान", "प्रभावित",
            # Weather emergency terms
            "cyclone approaching", "tsunami warning", "high tide", "storm coming",
            "waves hitting", "water level rising", "coastal flooding", "sea surge"
        ]

    def is_emergency_content(self, video: VideoInfo) -> bool:
        """
        Check if a video is emergency/distress content from individuals
        """
        # Combine title, description, and channel name for checking
        text_to_check = f"{video.title} {video.description} {video.channel}".lower()
        
        # First, exclude news channels and official content
        for channel in self.exclude_channels:
            if channel.lower() in text_to_check:
                return False
        
        # Exclude educational/informational content
        for exclude_word in self.exclude_content_keywords:
            if exclude_word.lower() in text_to_check:
                return False
        
        # Check for emergency/distress keywords
        emergency_score = 0
        for keyword in self.emergency_keywords:
            if keyword.lower() in text_to_check:
                emergency_score += 1
        
        # Must have at least 1 emergency keyword to be considered emergency content
        return emergency_score > 0

    def is_india_related(self, video: VideoInfo) -> bool:
        """
        Check if a video is related to Indian coastal regions
        """
        # Combine title, description, and channel name for checking
        text_to_check = f"{video.title} {video.description} {video.channel}".lower()
        
        # Check for Indian coastal keywords
        for keyword in self.indian_coastal_keywords:
            if keyword.lower() in text_to_check:
                return True
        
        return False

    def search_youtube(self, query: str, max_results: int = 20) -> List[VideoInfo]:
        """
        Search YouTube for emergency videos with real-time filtering
        """
        videos = []
        try:
            # Encode the search query with emergency-specific terms and recent filter
            encoded_query = urllib.parse.quote_plus(query)
            # Add sorting by upload date (recent) and include live videos
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=CAMSAhAB"  # Sort by upload date, this hour
            
            print(f"Searching for emergency content: {query}")
            response = self.session.get(search_url)
            
            if response.status_code != 200:
                print(f"Failed to fetch search results for query: {query}")
                return videos
            
            # Extract video data from the page
            all_videos = self.extract_video_info(response.text, max_results * 5)  # Get more to filter
            
            # Filter for India-related AND emergency content only
            emergency_videos = []
            for video in all_videos:
                if self.is_india_related(video) and self.is_emergency_content(video):
                    emergency_videos.append(video)
            
            # Return only the requested number of emergency videos
            videos = emergency_videos[:max_results]
            
            print(f"Found {len(all_videos)} total videos, {len(emergency_videos)} emergency videos, showing {len(videos)} for '{query}'")
            
            # Add delay to avoid being blocked
            time.sleep(3)
            
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")
        
        return videos

    def extract_video_info(self, html_content: str, max_results: int) -> List[VideoInfo]:
        """
        Extract video information from YouTube search page HTML
        """
        videos = []
        
        try:
            # Look for video data in the HTML
            # YouTube embeds video data in JavaScript
            script_pattern = r'var ytInitialData = ({.*?});'
            script_match = re.search(script_pattern, html_content)
            
            if not script_match:
                # Fallback to HTML parsing
                return self.extract_from_html(html_content, max_results)
            
            data_str = script_match.group(1)
            data = json.loads(data_str)
            
            # Navigate through YouTube's data structure
            contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
            
            for section in contents:
                if 'itemSectionRenderer' in section:
                    items = section['itemSectionRenderer'].get('contents', [])
                    
                    for item in items:
                        if 'videoRenderer' in item and len(videos) < max_results:
                            video_data = item['videoRenderer']
                            
                            # Extract video information
                            title = self.safe_extract_text(video_data.get('title', {}))
                            video_id = video_data.get('videoId', '')
                            url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
                            
                            channel_name = ""
                            if 'ownerText' in video_data:
                                channel_name = self.safe_extract_text(video_data['ownerText'])
                            
                            views = ""
                            if 'viewCountText' in video_data:
                                views = self.safe_extract_text(video_data['viewCountText'])
                            
                            upload_time = ""
                            if 'publishedTimeText' in video_data:
                                upload_time = self.safe_extract_text(video_data['publishedTimeText'])
                            
                            duration = ""
                            if 'lengthText' in video_data:
                                duration = self.safe_extract_text(video_data['lengthText'])
                            
                            thumbnail = ""
                            if 'thumbnail' in video_data and 'thumbnails' in video_data['thumbnail']:
                                thumbnails = video_data['thumbnail']['thumbnails']
                                if thumbnails:
                                    thumbnail = thumbnails[-1].get('url', '')
                            
                            description = ""
                            if 'descriptionSnippet' in video_data:
                                description = self.safe_extract_text(video_data['descriptionSnippet'])
                            
                            if title and url:
                                video = VideoInfo(
                                    title=title,
                                    url=url,
                                    channel=channel_name,
                                    views=views,
                                    upload_time=upload_time,
                                    duration=duration,
                                    thumbnail=thumbnail,
                                    description=description
                                )
                                videos.append(video)
        
        except Exception as e:
            print(f"Error extracting video info: {str(e)}")
            # Fallback to HTML parsing
            return self.extract_from_html(html_content, max_results)
        
        return videos

    def extract_from_html(self, html_content: str, max_results: int) -> List[VideoInfo]:
        """
        Fallback method to extract video info using BeautifulSoup
        """
        videos = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for video containers
        video_elements = soup.find_all('div', {'class': re.compile(r'ytd-video-renderer|ytd-compact-video-renderer')})
        
        for element in video_elements[:max_results]:
            try:
                title_elem = element.find('a', id='video-title') or element.find('h3')
                title = title_elem.get_text().strip() if title_elem else ""
                
                url = ""
                if title_elem and title_elem.get('href'):
                    url = "https://www.youtube.com" + title_elem['href']
                
                channel_elem = element.find('a', {'class': re.compile(r'channel-name|ytd-channel-name')})
                channel = channel_elem.get_text().strip() if channel_elem else ""
                
                if title and url:
                    video = VideoInfo(
                        title=title,
                        url=url,
                        channel=channel,
                        views="",
                        upload_time="",
                        duration="",
                        thumbnail="",
                        description=""
                    )
                    videos.append(video)
                    
            except Exception as e:
                continue
        
        return videos

    def safe_extract_text(self, text_obj):
        """
        Safely extract text from YouTube's text objects
        """
        if isinstance(text_obj, dict):
            if 'runs' in text_obj:
                return ''.join([run.get('text', '') for run in text_obj['runs']])
            elif 'simpleText' in text_obj:
                return text_obj['simpleText']
        elif isinstance(text_obj, str):
            return text_obj
        return ""

    def scrape_all_hazards(self, max_results_per_query: int = 10) -> Dict[str, List[VideoInfo]]:
        """
        Scrape emergency videos for ocean hazards in English and Hindi, focusing on live/recent distress content
        """
        all_results = {}
        
        print("Starting YouTube scraping for EMERGENCY ocean hazard content...")
        print("Focus: Live videos, distress calls, and recent emergency situations")
        print("Excluding: News channels, educational content, tourism videos")
        
        # Search for English emergency terms
        print("\n=== Searching for English Emergency Content ===")
        for hazard in self.hazards_english:
            # Create emergency-specific search queries
            emergency_queries = [
                f"{hazard} help rescue India live emergency",
                f"{hazard} flooding water rising India help",
                f"India {hazard} emergency evacuation live",
                f"{hazard} damage India affected people help",
                f"live {hazard} India coastal emergency now"
            ]
            
            combined_results = []
            for query in emergency_queries:
                results = self.search_youtube(query, max_results_per_query // len(emergency_queries) + 2)
                combined_results.extend(results)
            
            # Remove duplicates based on URL
            unique_results = []
            seen_urls = set()
            for video in combined_results:
                if video.url not in seen_urls:
                    unique_results.append(video)
                    seen_urls.add(video.url)
            
            # Limit to max_results_per_query
            all_results[f"english_{hazard}_emergency"] = unique_results[:max_results_per_query]
            print(f"Found {len(all_results[f'english_{hazard}_emergency'])} emergency videos for '{hazard}'")
        
        # Search for Hindi emergency terms
        print("\n=== Searching for Hindi Emergency Content ===")
        for hazard in self.hazards_hindi:
            # Create emergency-specific Hindi search queries
            hindi_emergency_queries = [
                f"{hazard} मदद बचाओ भारत लाइव आपातकाल",
                f"{hazard} बाढ़ पानी बढ़ रहा भारत मदद",
                f"भारत {hazard} आपातकाल निकासी लाइव",
                f"{hazard} नुकसान भारत प्रभावित लोग मदद",
                f"लाइव {hazard} भारत तटीय आपातकाल अभी"
            ]
            
            combined_results = []
            for query in hindi_emergency_queries:
                results = self.search_youtube(query, max_results_per_query // len(hindi_emergency_queries) + 2)
                combined_results.extend(results)
            
            # Remove duplicates based on URL
            unique_results = []
            seen_urls = set()
            for video in combined_results:
                if video.url not in seen_urls:
                    unique_results.append(video)
                    seen_urls.add(video.url)
            
            # Limit to max_results_per_query
            hazard_name = self.hazards_english[self.hazards_hindi.index(hazard)] if hazard in self.hazards_hindi else "unknown"
            all_results[f"hindi_{hazard_name}_emergency"] = unique_results[:max_results_per_query]
            print(f"Found {len(all_results[f'hindi_{hazard_name}_emergency'])} emergency videos for '{hazard}'")
        
        return all_results

    def save_to_csv(self, results: Dict[str, List[VideoInfo]], filename: str = "emergency_ocean_hazards_videos.csv"):
        """
        Save emergency video results to CSV file
        """
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['search_term', 'language', 'hazard_type', 'content_type', 'title', 'url', 'channel', 'views', 'upload_time', 'duration', 'thumbnail', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for search_term, videos in results.items():
                # Extract language and hazard type from search term
                if search_term.startswith('english_'):
                    language = 'English'
                    hazard_type = search_term.replace('english_', '').replace('_emergency', '')
                elif search_term.startswith('hindi_'):
                    language = 'Hindi'
                    hazard_type = search_term.replace('hindi_', '').replace('_emergency', '')
                else:
                    language = 'Unknown'
                    hazard_type = search_term
                
                for video in videos:
                    writer.writerow({
                        'search_term': search_term,
                        'language': language,
                        'hazard_type': hazard_type,
                        'content_type': 'Emergency/Distress',
                        'title': video.title,
                        'url': video.url,
                        'channel': video.channel,
                        'views': video.views,
                        'upload_time': video.upload_time,
                        'duration': video.duration,
                        'thumbnail': video.thumbnail,
                        'description': video.description
                    })
        
        print(f"\nEmergency video results saved to {filename}")

    def save_to_json(self, results: Dict[str, List[VideoInfo]], filename: str = "emergency_ocean_hazards_videos.json"):
        """
        Save emergency video results to JSON file with metadata
        """
        json_data = {
            "metadata": {
                "scrape_date": datetime.now().isoformat(),
                "focus": "Emergency/Distress videos from Indian coastal regions",
                "content_type": "Live streams, emergency calls, rescue videos",
                "excluded": "News channels, educational content, tourism videos",
                "languages": ["English", "Hindi"],
                "total_emergency_videos": sum(len(videos) for videos in results.values()),
                "search_categories": len(results),
                "time_filter": "Recent uploads and live content prioritized"
            },
            "results": {}
        }
        
        for search_term, videos in results.items():
            # Extract language and hazard type from search term
            if search_term.startswith('english_'):
                language = 'English'
                hazard_type = search_term.replace('english_', '').replace('_emergency', '')
            elif search_term.startswith('hindi_'):
                language = 'Hindi'
                hazard_type = search_term.replace('hindi_', '').replace('_emergency', '')
            else:
                language = 'Unknown'
                hazard_type = search_term
                
            json_data["results"][search_term] = {
                "language": language,
                "hazard_type": hazard_type,
                "content_type": "Emergency/Distress",
                "video_count": len(videos),
                "videos": [
                    {
                        'title': video.title,
                        'url': video.url,
                        'channel': video.channel,
                        'views': video.views,
                        'upload_time': video.upload_time,
                        'duration': video.duration,
                        'thumbnail': video.thumbnail,
                        'description': video.description
                    }
                    for video in videos
                ]
            }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Emergency video results saved to {filename}")

def main():
    # Create scraper instance
    scraper = YouTubeScraper()
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Scrape emergency videos for ocean hazards in English and Hindi only
    results = scraper.scrape_all_hazards(max_results_per_query=8)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"output/emergency_ocean_hazards_{timestamp}.csv"
    json_filename = f"output/emergency_ocean_hazards_{timestamp}.json"
    
    scraper.save_to_csv(results, csv_filename)
    scraper.save_to_json(results, json_filename)
    
    # Print summary
    total_videos = sum(len(videos) for videos in results.values())
    print(f"\n=== EMERGENCY CONTENT SCRAPING COMPLETE ===")
    print(f"Focus: EMERGENCY/DISTRESS videos from Indian coastal regions")
    print(f"Content Type: Live streams, rescue videos, emergency calls")
    print(f"Excluded: News channels, educational videos, tourism content")
    print(f"Languages: English and Hindi")
    print(f"Total emergency videos found: {total_videos}")
    print(f"Search categories: {len(results)}")
    print(f"Files saved:")
    print(f"  - {csv_filename}")
    print(f"  - {json_filename}")
    
    # Print breakdown by hazard type
    print(f"\nBreakdown by hazard type (Emergency content only):")
    for search_term, videos in results.items():
        if videos:  # Only show categories with results
            hazard = search_term.split('_')[1] if '_' in search_term else search_term
            language = search_term.split('_')[0] if '_' in search_term else 'unknown'
            print(f"  - {hazard} ({language}): {len(videos)} emergency videos")
    
    if total_videos == 0:
        print(f"\n⚠️  No emergency videos found. This could mean:")
        print(f"   • No current emergencies in Indian coastal areas")
        print(f"   • People may be using different platforms for emergency calls")
        print(f"   • Emergency content may be on private/restricted videos")
        print(f"   • Try running the scraper during actual weather events")

if __name__ == "__main__":
    main()