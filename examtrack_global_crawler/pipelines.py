# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
from dotenv import load_dotenv
import mysql.connector
from .items import UnivJournalItem, DaigakuinItem

# Load environment variables
load_dotenv()

class BasePipeline:
    def open_spider(self, spider):
        # initialize
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

class UnivJournalPipeline(BasePipeline):
    def process_item(self, item, spider):
        if isinstance(item, UnivJournalItem):
            # Check if item already exists
            self.cursor.execute(f"""
                SELECT EXISTS(SELECT 1 FROM {os.getenv('TABLE_NAME_UNIV_JOURNAL')} 
                WHERE grad_school_name = %s AND major = %s AND grad_school_url = %s)
                """, (item.get('grad_school_name'), item.get('major'), item.get('grad_school_url')))
            exists = self.cursor.fetchone()[0]
            if not exists:
                try:
                    self.cursor.execute(f"""
                        INSERT INTO {os.getenv('TABLE_NAME_UNIV_JOURNAL')} (grad_school_name, major, grad_school_url) 
                        VALUES (%s, %s, %s)
                        """, (item.get('grad_school_name'), item.get('major'), item.get('grad_school_url')))
                    self.connection.commit()
                except mysql.connector.Error as err:
                    spider.logger.error(f"Error inserting item: {item} - {err}")
            else:
                spider.logger.info(f"Duplicate item skipped: {item}")
            return item
        else:
            return item

class DaigakuinPipeline(BasePipeline):
    def process_item(self, item, spider):
        if isinstance(item, DaigakuinItem):
            try:
                self.cursor.execute(f"""
                    INSERT INTO {os.getenv('TABLE_NAME_DAIGAKUIN')} (grad_school_name, major, grad_school_url) 
                    VALUES (%s, %s, %s)
                    """, (item.get('grad_school_name'), item.get('major'), item.get('grad_school_url')))
                self.connection.commit()
            except mysql.connector.Error as err:
                spider.logger.error(f"Error inserting item: {item} - {err}")
            return item
        else:
            return item