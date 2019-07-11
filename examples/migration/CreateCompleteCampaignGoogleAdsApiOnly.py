#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This example creates serach campaign with the help of Google Ads API"""


"""This code example is the last in a series of code examples that shows how to create
a Search campign using the AdWords API, and then migrate it to the Google Ads API one
functionality at a time. See Step0.cs through Step5.cs for code examples in various stages
of migration.

This code example represents the final state, where all the functionality - create a
campaign budget, a Search campaign, ad groups, keywords and expanded text ads have been
migrated to using the Google Ads API. The AdWords API is not used.
"""


import datetime
import uuid
from googleads import adwords
import argparse
import collections
import sys
import six
from google.ads.google_ads.client import GoogleAdsClient
from google.ads.google_ads.errors import GoogleAdsException
#Number of ads being added/updated in this code example.
NUMBER_OF_ADS = 5
#The list of keywords being added in this code example.
KEYWORDS_TO_ADD = ["mars cruise", "space hotel" ]
import urllib.parse
PAGE_SIZE = 1000


def createCampaignBudget(client, customer_id):
    campaign_service = client.get_service('CampaignBudgetService')
    operation = client.get_type("CampaignBudgetOperation")
    criterion = operation.create
    criterion.name.value = 'Interplanetary Cruise Budget #%s' % uuid.uuid4()
    criterion.delivery_method = client.get_type("BudgetDeliveryMethodEnum").\
                                                STANDARD
    criterion.amount_micros.value = 500000
    response = campaign_service.mutate_campaign_budgets(customer_id, \
                                                        [operation])
    campaignBudgetResourceName = response.results[0].resource_name
    newCampaignBudget = getCampaignBudget(client, customer_id, \
                                          campaignBudgetResourceName)
    print("Added budget named {}".format(newCampaignBudget.name.value))
    return newCampaignBudget


def getCampaignBudget(client, customerId, resource_name):
    ga_service = client.get_service("GoogleAdsService")
    query = ("SELECT campaign_budget.id, campaign_budget.name, "
             "campaign_budget.resource_name FROM campaign_budget WHERE "
             "campaign_budget.resource_name = '%s' "%resource_name)
    response = ga_service.search(customerId, query, PAGE_SIZE)
    budget = list(response)[0].campaign_budget
    return budget


def createCampaign(client, customerId, campaignBudget): 
    operation = client.get_type("CampaignOperation")
    campaign = operation.create
    campaign_service = client.get_service("CampaignService")
    campaign.name.value = 'Interplanetary Cruise#%s' % uuid.uuid4()
    campaign.advertising_channel_type = client.get_type\
                                        ("AdvertisingChannelTypeEnum").SEARCH
    # Recommendation: Set the campaign to PAUSED when creating it to stop the
    # ads from immediately serving. Set to ENABLED once you've added
    # targeting and the ads are ready to serve.
    campaign.status = client.get_type("CampaignStatusEnum").PAUSED
    campaign.manual_cpc.enhanced_cpc_enabled.value = True
    campaign.campaign_budget.value = campaignBudget.resource_name
    campaign.network_settings.target_google_search.value = True
    campaign.network_settings.target_search_network.value =True
    campaign.network_settings.target_content_network.value =False
    campaign.network_settings.target_partner_search_network.value =False
    campaign.start_date.value =  (datetime.datetime.now() + \
                                    datetime.timedelta(1)).strftime('%Y%m%d')
    campaign.end_date.value = (datetime.datetime.now() + \
                              datetime.timedelta(365)).strftime('%Y%m%d')
    response = campaign_service.mutate_campaigns(customerId, [operation])
    campaignResourceName = response.results[0].resource_name
    newCampaign = getCampaign(client, customerId, campaignResourceName)
    print("Added campaign named {}".format(newCampaign.name.value))
    return newCampaign


def getCampaign(client, customerId, campaignResourceName):
    ga_service = client.get_service("GoogleAdsService")
    query = ("SELECT campaign.id,campaign.name, campaign.resource_name "
            "FROM campaign WHERE campaign.resource_name = '%s' "%
            campaignResourceName)
    response = ga_service.search(customerId, query, PAGE_SIZE)
    campaign = list(response)[0].campaign
    return campaign


def createAdGroup(client, customerId, campaign):
    operation = client.get_type("AdGroupOperation")
    adgroup = operation.create
    adgroup_service = client.get_service("AdGroupService")
    adgroup.name.value  = 'Earth to Mars Cruises #%s'% uuid.uuid4()
    adgroup.campaign.value = campaign.resource_name 
    adgroup.status = client.get_type("AdGroupStatusEnum").ENABLED
    adgroup.type = client.get_type("AdGroupTypeEnum").SEARCH_STANDARD
    adgroup.cpc_bid_micros.value = 10000000  
    response = adgroup_service.mutate_ad_groups(customerId, [operation])
    adGroupResourceName = response.results[0].resource_name
    adGroup = getAdGroup(client, customerId, adGroupResourceName)
    print("Added AdGroup named {}".format(adGroup.name.value))
    return adGroup


def getAdGroup(client, customerId, adGroupResourceName):
    ga_service = client.get_service("GoogleAdsService")
    query = ("SELECT ad_group.id, ad_group.name, ad_group.resource_name "
          "FROM ad_group WHERE ad_group.resource_name = '%s' "\
          %adGroupResourceName)
    response = ga_service.search(customerId, query, PAGE_SIZE)
    adGroup = list(response)[0].ad_group
    return adGroup


def createTextAds(client, customerId, adGroup):
    operations = []
    for i in range(0,NUMBER_OF_ADS):
        operation = client.get_type("AdGroupAdOperation")
        AdGroupOperation = operation.create
        AdGroupOperation.ad_group.value =  adGroup.resource_name 
        AdGroupOperation.status = client.get_type("AdGroupAdStatusEnum").PAUSED
        AdGroupOperation.ad.expanded_text_ad.headline_part1.value = \
                                    'Cruise to Mars #%s'% str(uuid.uuid4())[:4]
        AdGroupOperation.ad.expanded_text_ad.headline_part2.value = \
                                    'Best Space Cruise Line'
        AdGroupOperation.ad.expanded_text_ad.description.value = \
                                    'Buy your tickets now!'
        final_urls =  client.get_type("StringValue")
        final_urls.value = 'http://www.example.com'
        AdGroupOperation.ad.final_urls.extend([final_urls])
        operations.append(operation)
    adgroup_service = client.get_service("AdGroupAdService")
    adGroupAdResponse = adgroup_service.mutate_ad_group_ads(customerId, \
                                                            operations)
    newAdResourceNames = []
    for i in range(NUMBER_OF_ADS):
        newAdResourceNames.append(adGroupAdResponse.results[i].resource_name)

    newAds = getAds(client, customerId, newAdResourceNames)
    for i in range(len(newAds)):
        print("Created expanded text ad with ID {}, status {} and "
               "headline {}.{}".\
        format(newAds[i].ad.id.value,\
        newAds[i].status,newAds[i].ad.expanded_text_ad.headline_part1.value,\
        newAds[i].ad.expanded_text_ad.headline_part2.value))


def getAds(client, customerId, newAdResourceNames):
    #Prepares the query in the form of the string 'Resource1.name','Resource2.name'
    #for the in clause
    def formatter(myst):
        results =[]
        for i in myst:
            results.append(repr(i))
        return ','.join(results)
    resouceNames = formatter(newAdResourceNames)
  
    ga_service = client.get_service("GoogleAdsService")
    query = ("SELECT ad_group_ad.ad.id, " 
             "ad_group_ad.ad.expanded_text_ad.headline_part1, " 
             "ad_group_ad.ad.expanded_text_ad.headline_part2, " 
             "ad_group_ad.status, ad_group_ad.ad.final_urls, " 
             "ad_group_ad.resource_name " 
             "FROM ad_group_ad " 
             "WHERE ad_group_ad.resource_name in (%s)"%(resouceNames))
    response = ga_service.search(customerId, query, PAGE_SIZE)
    adGroup = list(response)
    ads = []
    for i in range(len(adGroup)):
        ads.append(adGroup[i].ad_group_ad)
    return ads


def createKeywords(client, customerId, adGroup, keywordstoadd):
    adGroupCriterionOperations = []
    for keyword in keywordstoadd:
        operation = client.get_type("AdGroupCriterionOperation")
        AdGroupCriterionOperation = operation.create
        AdGroupCriterionOperation.ad_group.value = adGroup.resource_name
        AdGroupCriterionOperation.status = client.get_type\
                                        ("AdGroupCriterionStatusEnum").ENABLED
        AdGroupCriterionOperation.keyword.text.value = keyword 
        AdGroupCriterionOperation.keyword.match_type = client.get_type\
                                        ("KeywordMatchTypeEnum").EXACT
        adGroupCriterionOperations.append(operation)
    adGroupCriterionServiceClient = client.get_service\
                                        ("AdGroupCriterionService")
    adGroupCriterionResponse = adGroupCriterionServiceClient.\
                mutate_ad_group_criteria(customerId,adGroupCriterionOperations)
    newAdResourceNames = []
    for i in range(len(keywordstoadd)):
        newAdResourceNames.append\
        (adGroupCriterionResponse.results[i].resource_name)
    newKeywords = getKeywords(client, customerId, newAdResourceNames)
    for i in range(len(newKeywords)):
        print("Keyword with text {}, id = {} and match type {} was created".\
        format(newKeywords[i].keyword.text.value, \
        newKeywords[i].criterion_id.value, newKeywords[i].keyword.match_type))


def getKeywords(client, customerId, keywordResourceNames): 
    def formatter(myst):
        results =[]
        for i in myst:
            results.append(repr(i))
        return ','.join(results)
    resouceNames = formatter(keywordResourceNames)
    ga_service = client.get_service("GoogleAdsService")
    query = ("SELECT ad_group.id, ad_group.status, "
    "ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
    "ad_group_criterion.keyword.match_type FROM ad_group_criterion " 
    "WHERE ad_group_criterion.type = 'KEYWORD' " 
    "AND ad_group.status = 'ENABLED' " 
    "AND ad_group_criterion.status IN ('ENABLED', 'PAUSED') " 
    "AND ad_group_criterion.resource_name IN (%s)"%(resouceNames))
    response = ga_service.search(customerId, query, PAGE_SIZE)
    adGroupCriterion = list(response)
    keywords = []
    for i in range(len(adGroupCriterion)):
        keywords.append(adGroupCriterion[i].ad_group_criterion)
    return keywords


if __name__ == '__main__':
  # Initialize client object.
  #It will read the config file. Default file path is the Home Directory
  google_ads_client = GoogleAdsClient.load_from_storage()
  adwords_client = adwords.AdWordsClient.LoadFromStorage()

  parser = argparse.ArgumentParser(
        description='Lists all campaigns for specified customer.')
    # The following argument(s) should be provided to run the example.
  parser.add_argument('-c', '--customer_id', type=six.text_type,
                        required=True, help='The Google Ads customer ID.')
  args = parser.parse_args()
  budget = createCampaignBudget(google_ads_client, args.customer_id)
  campaign = createCampaign(google_ads_client, args.customer_id, budget)
  adGroup = createAdGroup(google_ads_client, args.customer_id, campaign)
  createTextAds(google_ads_client, args.customer_id, adGroup)
  createKeywords(google_ads_client, args.customer_id, adGroup, KEYWORDS_TO_ADD)

