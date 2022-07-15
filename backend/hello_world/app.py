import json
import os
import logging
import boto3
from botocore.exceptions import ClientError
import pandas as pd
import openpyxl
import numpy as np
import math
from scipy.stats import norm
#import norm

# Handle logger
logger = logging.getLogger()
logger.setLevel(logging.os.environ['LOG_LEVEL'])

dynamodb = boto3.resource('dynamodb')
aws_environment = os.environ['AWSENV']

logger.info("Finished handling variables, imports, and clients")

# Check if executing locally or on AWS, and configure DynamoDB connection accordingly.
# https://github.com/ganshan/sam-dynamodb-local/blob/master/src/Person.py
if aws_environment == "AWS_SAM_LOCAL":
    table = boto3.resource('dynamodb', endpoint_url="http://dynamodb-local:8000").Table('visitorCount') #Local table name hard coded in entrypoint.sh for local dev
    logger.info("Using local Dynamo container for testing")
else: # Running in AWS
    table = dynamodb.Table(os.environ['TABLE_NAME'])

logger.info("Finished conditional dynamodb logic")

def getUserCount():
    try:
        logger.info("Querying DDB")
        user_count_from_table = table.get_item(
            Key={'Count': 'Users'}
        )

        #Handle first use case where count doesn't exist yet
        if 'Item' in user_count_from_table:
            user_count = user_count_from_table['Item']['Number'] +1
        else: 
            user_count = 1
        logger.info(user_count)

        return user_count

    #Catch known errors
    #ToDo: Add more handling here
    except ClientError as e:
        if e.response['Error']['Code'] == 'RequestLimitExceeded':
            logger.error('ERROR: ', e)
        else:
            logger.error("UNEXPECTED ERROR from DDB: %s" % e)

def updateUserCount(count):
    try:
        logger.info("Updating DDB with new user count")
        table.put_item(
            Item={
                'Count': 'Users',
                'Number': count
            }
        )

    #Catch known errors
    #ToDo: Add more handling here
    except ClientError as e:
        if e.response['Error']['Code'] == 'RequestLimitExceeded':
            logger.error('ERROR: ', e)
        else:
            logger.error("UNEXPECTED ERROR from DDB: %s" % e)


#Function for AWS that does all the math
def genMat(RID, MVAL, BlockSize):
    
    #Reads Data In
    dataSheet = pd.read_excel(r'dataDLOM.xlsx', sheet_name='Sheet1')
    dataSheetColumnNames = dataSheet.columns.tolist()
    dataSheet=dataSheet.to_numpy()
    dataSheetLength = dataSheet.shape[0]
    dataSheetWidth = dataSheet.shape[1]

    #Declares a few variables as set up
    DISCAASPMat = []
    DISCBSPMat = []
    DISCLBPMat = []
    tFactor = math.log(100) - math.log(100-BlockSize)
    display = 0

    #Find row where RID == ymrt
    i=0
    while i < dataSheetLength:
        if dataSheet[i][0] == RID:
            # If MVAL is not within bounds then break
            if MVAL > dataSheet[i][3]:
                logger.info("MVAL is too high. Please change to fit inside bounds ")
                # print('MVAL is too high. Please change to fit inside bounds ', dataSheet[i][2],' - ',dataSheet[i+9][3])
            elif MVAL < dataSheet[i+9][2]:
                logger.info("MVAL is too low. Please change to fit inside bounds ")
                # print('MVAL is too low. Please change to fit inside bounds ', dataSheet[i][2],' - ',dataSheet[i][3])
            else:
                logger.info("Date is: "+str(RID))
                logger.info("MVAL is: "+str(MVAL))
                logger.info("Block Size is: "+str(BlockSize))
                i = findMVALIndex(i, dataSheet)
                display = 1
                t1 = tFactor*dataSheet[i][8]   #h-life Mean * tFactor
                sigma = dataSheet[i][4] #Sig Mean
                sigsqt = t1*(sigma)**2
                sigsqrtt = math.sqrt(sigsqt)
                d1 = sigsqrtt/(4*math.sqrt(3))
                d2 = -3*d1
                v1 = math.exp(sigsqt)
                v2 = sigsqt + (math.log(2 * (v1 - sigsqt - 1))) - (2 * math.log(v1 - 1))
                v3 = math.sqrt(v2 / t1)
                v4 = v3 * math.sqrt(t1)

                EXAASP = 2 * norm.cdf(v4 / 2)
                EXBSP = 2 * norm.cdf(sigsqrtt / 2)
                EXLBP = (2+sigsqt/2)* norm.cdf(sigsqrtt/2)+(math.sqrt(sigsqt*7/44))*(math.exp(-sigsqt/8))

                DISCAASPMean = (EXAASP - 1) / EXAASP
                DISCBSPMean = (EXBSP - 1) / EXBSP
                DISCLBPMean = (EXLBP - 1) / EXLBP

                ## Looping the 3x3 array
                SIGArray = [dataSheet[i][5], dataSheet[i][6], dataSheet[i][7]]
                hlifeArray = [dataSheet[i][9], dataSheet[i][10], dataSheet[i][11]]
                for x in SIGArray:
                    for y in hlifeArray:
                        t1 = tFactor*y  # h-life * tFactor
                        sigma = x  # Sig
                        sigsqt = t1*(sigma)**2
                        sigsqrtt = math.sqrt(sigsqt)
                        d1 = sigsqrtt / (4 * math.sqrt(3))
                        d2 = -3 * d1
                        v1 = math.exp(sigsqt)
                        v2 = sigsqt + (math.log(2 * (v1 - sigsqt - 1))) - (2 * math.log(v1 - 1))
                        v3 = math.sqrt(v2 / t1)
                        v4 = v3 * math.sqrt(t1)

                        EXAASP = 2 * norm.cdf(v4 / 2)
                        EXBSP = 2 * norm.cdf(sigsqrtt / 2)
                        EXLBP = (2 + sigsqt / 2) * norm.cdf(sigsqrtt / 2) + (math.sqrt(sigsqt * 7 / 44)) * (
                            math.exp(-sigsqt / 8))

                        DISCAASP = (EXAASP - 1) / EXAASP
                        DISCBSP = (EXBSP - 1) / EXBSP
                        DISCLBP = (EXLBP - 1) / EXLBP

                        DISCAASPMat.append(DISCAASP)
                        DISCBSPMat.append(DISCBSP)
                        DISCLBPMat.append(DISCLBP)

            break
        i=i+1

    if display == 1 :
        DISCAASPMat = np.reshape(DISCAASPMat, (-1, 3))
        DISCBSPMat = np.reshape(DISCBSPMat, (-1, 3))
        DISCLBPMat = np.reshape(DISCLBPMat, (-1, 3))

    return DISCAASPMat, DISCBSPMat, DISCLBPMat, DISCAASPMean, DISCBSPMean, DISCLBPMean;

def extract_child_from_body_of_apg_event(event, child_item, mandatory): 
    try:
        passed_value = event['multiValueQueryStringParameters'][child_item][0]
        return passed_value
    except (KeyError, json.decoder.JSONDecodeError, TypeError) as e: #If passed value is empty then throw an error
        if(mandatory):
            logger.error(f"Could not find value for: {child_item}")
            raise 'ERROR: Must pass in all required values!'

def lambda_handler(event, context):
    RID=extract_child_from_body_of_apg_event(event, 'RID', mandatory=True)
    MVAL=extract_child_from_body_of_apg_event(event, 'MVAL', mandatory=True)
    BlockSize=extract_child_from_body_of_apg_event(event, 'BlockSize', mandatory=True)
    RID=RID.replace('-','')
    RID=int(RID)
    BlockSize=int(BlockSize)
    MVAL=int(MVAL)
    logger.info("RID: "+str(RID))
    logger.info("BlockSize: "+str(BlockSize))
    logger.info("MVAL: "+str(MVAL))
    logger.info(type(MVAL))

    user_count = getUserCount()
    updateUserCount(user_count)
    DISCAASPMat, DISCBSPMat, DISCLBPMat, DISCAASPMean, DISCBSPMean, DISCLBPMean = genMat(RID, MVAL, BlockSize)
    logger.info("DISCAASPMean: "+str(DISCAASPMean))
    logger.info("DISCBSPMean: "+str(DISCBSPMean))
    logger.info("DISCLBPMean: "+str(DISCLBPMean))
    logger.info("User count: "+str(user_count))
    DISCAASPMat = DISCAASPMat.tolist()
    logger.info(DISCAASPMat)
    DISCBSPMat = DISCBSPMat.tolist()
    logger.info(DISCBSPMat)
    DISCLBPMat = DISCLBPMat.tolist()
    logger.info(DISCLBPMat)


    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "User count": str(user_count),
            "DISCAASPMat": DISCAASPMat,
            "DISCBSPMat": DISCBSPMat,
            "DISCLBPMat": DISCLBPMat,
            "DISCAASPMean": str(DISCAASPMean),
            "DISCBSPMean": str(DISCBSPMean),
            "DISCLBPMean": str(DISCLBPMean)
        }),
    }
