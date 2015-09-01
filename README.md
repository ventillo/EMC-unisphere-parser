# EMC-unisphere-parser
NAME
    vmax.py - CLI tool gathering performance / other data from an EMC unisphere.

SYNOPSIS
    vmax.py -mode <CHECK|DET|LIST|FAS|DAS|X> 
            [-sid <Symmetrix_ID>] 
            [-spa <EMC_unisphere_address> 
            [-time <#hours>] 
            [-fa <FA_PORT>] 
            [-da <DA_PORT>]    

DESCRIPTION
    Options and functionality:

    -mode  This switch controls the main functionality of the script 
           (i.e. which part of the unisphere we want to see). It accepts several 
           predefined arguments.

    -mode CHECK
           Checks for Unispheres and Arrays defined on AT&T web page
           http://sanmobility.edc.cingular.net/storage_ops/tools/accessemc.html
           Then cycles through all available resources and checks for a 24-hour
           period worth of data. A simple check to see if data is being 
           collected. Records are in 5 minute intervals - 287 records = 24 hrs.

    -mode LIST [-spa <EMC_unisphere_address>]
           Lists all available storage arrays defined in unisphere. If -spa is 
           not given, again checks all defined unispheres in 
           http://sanmobility.edc.cingular.net/storage_ops/tools/accessemc.html

    -mode DET -sid <Symmetrix_ID> 
              -fa <FA_PORT> | -da <DA_PORT> 
              [-time <#hours>]
              [-spa <EMC_unisphere_address>]
           Detailed performance information of a specific FA or DA port
    
    -mode FAS -sid <Symmetrix_ID>
              [-time <#hours>]
              [-spa <EMC_unisphere_address>]
           List FA ports for a specific array

    -mode DAS -sid <Symmetrix_ID>
              [-time <#hours>]
              [-spa <EMC_unisphere_address>]
           List DA ports for a specific array

    -mode X -sid <Symmetrix_ID>
            [-time <#hours>]
            [-spa <EMC_unisphere_address>]
           Brief performance health check. Includes response times and Write 
           pending %
           
    Argument explanation and details:
    
    -spa   Unisphere address in format https://10.0.0.1:8443/spa or /univmax
           If you specify the -spa, it implies you use the full SID in -sid
           as well. Partial SIDs can only work within AT&T environment

    -sid   Partial or full Symmetrix ID number (e.g. 0622, 000195701639 ...)
           When using with conjunction with -spa, the full SID has to be
           defined

    -time  Time frame in hours until now. Last record is always current time.
           In simple terms, how many hours you want to go back in the report
    -fa    FA port ID. Format: FA-2G
    -da    DA port ID. Format: DA-1A

EXAMPLES
    vmax.py -sid 1639 -mode DET -fa FA-2G -time 24
    vmax.py -mode CHECK
    vmax.py -mode LIST -spa https://ulpd150.madc.att.com:8443/univmax
    vmax.py -mode X -sid 5024

SEE ALSO
    EMC.com 
