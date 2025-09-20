#!/usr/bin/env node
/**
 * Debug scraper to understand the actual HTML structure
 */

const https = require('https');
const fs = require('fs').promises;
const path = require('path');
const cheerio = require('cheerio');

class DebugScraper {
  constructor() {
    this.headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
    };
  }

  async fetchPage(url) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      
      const options = {
        hostname: urlObj.hostname,
        path: urlObj.pathname + urlObj.search,
        headers: this.headers,
        timeout: 30000
      };
      
      const req = https.request(options, (res) => {
        let data = '';
        
        res.on('data', chunk => {
          data += chunk;
        });
        
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
          }
        });
      });
      
      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      req.end();
    });
  }

  async debugPage(url, title) {
    console.log(`\n🔍 Debugging: ${title}`);
    console.log(`URL: ${url}`);
    
    try {
      const html = await this.fetchPage(url);
      const $ = cheerio.load(html);
      
      // Save full HTML for inspection
      const filename = title.replace(/[^a-zA-Z0-9]/g, '_') + '.html';
      await fs.writeFile(path.join(__dirname, '..', 'data', filename), html);
      
      console.log(`✓ HTML saved to: data/${filename}`);
      console.log(`✓ Page length: ${html.length} characters`);
      console.log(`✓ Page title: ${$('title').text()}`);
      
      // Check for various course patterns
      const coursePatterns = [
        /CS\s*(\d{5})/g,
        /CS(\d{5})/g,
        /CS-(\d{5})/g,
        /CS_(\d{5})/g
      ];
      
      let coursesFound = 0;
      
      coursePatterns.forEach((pattern, index) => {
        const matches = html.match(pattern);
        if (matches) {
          console.log(`✓ Pattern ${index + 1}: Found ${matches.length} matches`);
          console.log(`   Examples: ${matches.slice(0, 5).join(', ')}`);
          coursesFound += matches.length;
        }
      });
      
      console.log(`✓ Total course mentions: ${coursesFound}`);
      
      // Check for common HTML structures
      const structures = [
        { name: 'Tables', selector: 'table' },
        { name: 'Lists', selector: 'ul, ol' },
        { name: 'Divs', selector: 'div' },
        { name: 'Paragraphs', selector: 'p' }
      ];
      
      structures.forEach(structure => {
        const count = $(structure.selector).length;
        console.log(`✓ ${structure.name}: ${count} elements`);
      });
      
      // Look for specific course information
      const courseElements = [];
      
      $('*').each((i, element) => {
        const text = $(element).text();
        if (text.match(/CS\s*\d{5}/)) {
          courseElements.push({
            tag: element.tagName,
            text: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
            classes: $(element).attr('class') || '',
            id: $(element).attr('id') || ''
          });
        }
      });
      
      if (courseElements.length > 0) {
        console.log(`✓ Found ${courseElements.length} elements with course codes:`);
        courseElements.slice(0, 5).forEach((elem, i) => {
          console.log(`   ${i + 1}. <${elem.tag}> "${elem.text}"`);
        });
      }
      
      return { html, $ };
      
    } catch (error) {
      console.error(`❌ Error debugging ${title}:`, error.message);
      return null;
    }
  }

  async runDebug() {
    console.log('🔍 Debug Scraper - Analyzing Real Purdue CS Pages');
    console.log('=' * 60);
    
    const pages = [
      {
        url: 'https://www.cs.purdue.edu/undergraduate/curriculum/bachelor.html',
        title: 'Bachelor Curriculum'
      },
      {
        url: 'https://www.cs.purdue.edu/academic-programs/courses/2024_fall_courses.html',
        title: 'Fall 2024 Courses'
      },
      {
        url: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-mI-fall2023.html',
        title: 'Machine Intelligence Track'
      },
      {
        url: 'https://www.cs.purdue.edu/undergraduate/curriculum/track-softengr-fall2023.html',
        title: 'Software Engineering Track'
      }
    ];
    
    // Create data directory
    await fs.mkdir(path.join(__dirname, '..', 'data'), { recursive: true });
    
    for (const page of pages) {
      const result = await this.debugPage(page.url, page.title);
      if (result) {
        // Add small delay between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    console.log('\n🎉 Debug analysis complete!');
    console.log('Check the data/ directory for saved HTML files');
  }
}

// Run debug if called directly
if (require.main === module) {
  const debugScraper = new DebugScraper();
  debugScraper.runDebug().catch(console.error);
}

module.exports = DebugScraper;