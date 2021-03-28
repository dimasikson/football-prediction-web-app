
// #######################    main script    ##################################
// #######################    global constants    ##################################

var league = 'E0';
const fname = 'static/predicted.txt';

const monthsConvert = {
    '01': 'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'May',
    '06': 'Jun',
    '07': 'Jul',
    '08': 'Aug',
    '09': 'Sep',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec'
}

const teamNameChange = {
    "Fortuna Dusseldorf":"Fortuna",
    "Union Berlin":"Union B.",
    "Bayern Munich":"Bayern",
    "Werder Bremen":"Werder",
    "Ein Frankfurt": "Eintracht",
    "Leverkusen": "Bayer 04",
    "Crystal Palace":"C. Palace",
    "Sheffield United":"Sheffield",
    "Bournemouth":"Bmouth",
    "Southampton":"Soton",
    "Tottenham": "Spurs",
    "Man United": "Man Utd",
    "Sheffield Weds": "Shf. Weds",
    "Nott'm Forest": "Ntm Forest",
    "Huddersfield": "Huderrsf",
    "Middlesbrough": "Mbrough",
    "PSV Eindhoven": "PSV",
    "Sparta Rotterdam": "Sparta R",
    "Pacos Ferreira": "Pacos F",
    "Santa Clara": "Santa C"
};

// #######################    load predicted.txt    ##################################

var json = null;
function loadJSON() {
    $.ajax({
        'type': 'GET',
        'async': false,
        'global': false,
        'url': fname,
        'dataType': "text",
        'cache': false,
        'success': function (data) {
            json = data;
        }
    });
    return JSON.parse(json);
};

json = loadJSON();

// #######################    set global mobileFlag variable    ##################################

function isMobileDevice() {
    return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
};

var mobileFlag = isMobileDevice();

// if iPad, change mobileFlag = false;
if (window.navigator.userAgent.search('iPad') != -1){
    mobileFlag = false;
};

// #######################    util functions go here vvv    ##################################

function onlyUnique(value, index, self) { 
    return self.indexOf(value) === index;
}

// #######################    routine for loading matches into left tab    ##################################

var loadMatches = function (json, league) {

    var jsonFilteredGames = {};

    for (var i in json){

        if (json[i]['Div'] == league || league == 'W0'){
            jsonFilteredGames[i] = json[i]
        };

    };

    var matchDates = [];

    for (var i in jsonFilteredGames){
        matchDates.push(jsonFilteredGames[i]['Date'].split(' ')[0]);
    };

    matchDates = matchDates.filter(onlyUnique);
    matchDates.sort()
    matchDates.reverse();

    document.getElementById("resultsMenuGames").innerHTML = '';

    var countGamesDate = {};
    var countWinsDate = {};
    var sumReturnDate = {};

    for (var i = 0; i < matchDates.length; i++){

        var node = document.createElement("div");

        countGamesDate[matchDates[i]] = 0;
        countWinsDate[matchDates[i]] = 0;
        sumReturnDate[matchDates[i]] = 0;

        var dateSplit = matchDates[i].split('-');
        var dateDisplay = parseInt(dateSplit[2]) + " " + monthsConvert[dateSplit[1]] + " " + dateSplit[0];

        var textnode = document.createElement('span');
        textnode.innerHTML = dateDisplay;

        var nodeDiv = document.createElement("div");
        nodeDiv.appendChild(textnode);

        var spanROI = document.createElement("span");
        spanROI.classList.add('dateROI');
        spanROI.id = 'date:' + matchDates[i] + ':ROI';
        nodeDiv.appendChild(spanROI);

        node.appendChild(nodeDiv);
        node.classList.add('dateNode');
        node.id = 'date:' + matchDates[i];

        document.getElementById("resultsMenuGames").appendChild(node);

    }

    var countGames = {'H':0,'D':0,'A':0};
    var countWins = {'H':0,'D':0,'A':0};
    var sumReturn = {'H':0,'D':0,'A':0};

    for (var i in jsonFilteredGames){
        var matchDate = jsonFilteredGames[i]['Date'].split(' ')[0];

        var hTeam = jsonFilteredGames[i]['HomeTeam'];
        var aTeam = jsonFilteredGames[i]['AwayTeam'];

        if (hTeam in teamNameChange){
            hTeam = teamNameChange[hTeam]
        };
        if (aTeam in teamNameChange){
            aTeam = teamNameChange[aTeam]
        };

        var node = document.createElement("button");
        var nodeDiv = document.createElement("div");

        node.classList.add('button');
        node.id = 'game:' + i.toString();
        node.addEventListener('click', matchButtonsOnClick);

        var resultColorSpanH = document.createElement("span");
        var resultColorSpanD = document.createElement("span");
        var resultColorSpanA = document.createElement("span");

        var spans = [resultColorSpanH, resultColorSpanD, resultColorSpanA];
        var HDA = ['H', 'D', 'A'];

        for (var idx in spans){

            spans[idx].id = node.id + ':' + HDA[idx];
            spans[idx].classList.add('resultColorSpan');
            spans[idx].style.backgroundColor = '#36454f';
            spans[idx].style.color = '#ffffff';
            spans[idx].innerHTML = HDA[idx];
            spans[idx].style.border = '2px solid #4f565a'
            spans[idx].style.fontSize = '15px'

        };

        // returns tab

        var predResult;

        const lookupOdds = {
            'H': 'HomeOdds',
            'D': 'DrawOdds',
            'A': 'AwayOdds'
        }

        if (jsonFilteredGames[i]['preds'] >= 0.05) {
            predResult = 'H'
        } else if (jsonFilteredGames[i]['preds'] <= -0.05){
            predResult = 'A'
        } else {
            predResult = 'D'
        };

        if (jsonFilteredGames[i]['FTR'] != 0){

            countGames[predResult]++;
            countGamesDate[matchDate]++;

            spans[HDA.indexOf(jsonFilteredGames[i]['FTR'])].style.border = '2px solid #999999';

            var borderColor = '#fd3772';

            if (jsonFilteredGames[i]['FTR'] == predResult){
                
                countWins[predResult]++;
                countWinsDate[matchDate]++;

                sumReturn[predResult] = sumReturn[predResult] + jsonFilteredGames[i][lookupOdds[predResult]]*20;
                sumReturnDate[matchDate] = sumReturnDate[matchDate] + jsonFilteredGames[i][lookupOdds[predResult]]*20;

                borderColor = '#42ffa7';

            }
                
            sumReturn[predResult]--;
            sumReturnDate[matchDate]--;

            spans[HDA.indexOf(predResult)].style.border = '2px solid ' + borderColor;

        } else {

            spans[HDA.indexOf(predResult)].style.border = '2px solid #eeff90';

        };

        var teamNamesSpan = document.createElement("span");
        teamNamesSpan.innerHTML = hTeam + ' - ' + aTeam;
        teamNamesSpan.style.marginLeft = '5px';
        teamNamesSpan.id = node.id;

        node.appendChild(resultColorSpanH);
        node.appendChild(resultColorSpanD);
        node.appendChild(resultColorSpanA);
        node.appendChild(teamNamesSpan);

        nodeDiv.appendChild(node);        
        document.getElementById('date:' + matchDate).appendChild(nodeDiv);

    };


    var HDA = ['H', 'D', 'A', 'TTL'];

    for (var i in HDA){

        var returns;
        var acc;
        var count;


        if ( HDA[i] == 'TTL' ) {

            count = countGames['H']+countGames['D']+countGames['A'];    
            returns = Math.round( (sumReturn['H']+sumReturn['D']+sumReturn['A'])*100 / count );
            acc = Math.round( (countWins['H']+countWins['D']+countWins['A'])*100 / count );

        } else {

            count = countGames[HDA[i]];    
            returns = Math.round(sumReturn[HDA[i]]*100/count);
            acc = Math.round(countWins[HDA[i]]*100/count);

        }

        if (returns>=0){
            var colorRet = '#42ffa7';
            var signRet = '+';
        } else {
            var colorRet = '#fd3772';
            var signRet = '-';
        }

        $('#valAcc'+HDA[i]).html(
            acc+'%'
        );

        $('#valGames'+HDA[i]).html(
            count
        );

        $('#valROI'+HDA[i]).html(
            signRet+Math.abs(returns)+'%'
        );
        $('#valROI'+HDA[i]).css('color',colorRet);

    }

    for (var i in countGamesDate){

        var dateROItext;
        var colorRet = '#eeff90';

        if (countGamesDate[i]==0){
            dateROItext = 'Upcoming';
        } else {

            var returnDate = Math.round(sumReturnDate[i]*100/countGamesDate[i])
            var accuracyDate = Math.round(countWinsDate[i]*100/countGamesDate[i])

            if (returnDate>=0){
                var colorRet = '#42ffa7';
                var signRetDate = '+';
            } else {
                var colorRet = '#fd3772';
                var signRetDate = '-';    
            }

            dateROItext = signRetDate + Math.abs(returnDate) + '% ROI';
            // dateROItext = dateROItext + ', ' + accuracyDate + '% Acc';
            // dateROItext = dateROItext + ', ' + countGamesDate[i] + ' Game(s)';

        }

        document.getElementById('date:'+i+':ROI').innerHTML = dateROItext;
        document.getElementById('date:'+i+':ROI').style.color = colorRet;

    }


    $('.button').hover(
        function () {							

            $(this).animate({
                backgroundColor: "#4f565a"
            }, 100 );

            $(this).children().animate({
                backgroundColor: "#4f565a"
            }, 100 );

            $(this).css('cursor','pointer');

        },
        function () {

            $(this).animate({
                backgroundColor: "#36454f"
            }, 100 );

            $(this).children().animate({
                backgroundColor: "#36454f"
            }, 100 );

        }
    );

}

// #######################    routine for displaying prediction tab    ##################################

const matchButtonsOnClick = function(event) {

    $('#predictionTab').show();

    if (mobileFlag==true){
        $('#resultsMenu').hide();
    }

    var scrollThr = 300;

    if (document.body.scrollTop > scrollThr || document.documentElement.scrollTop > scrollThr) {

        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera  

    }
    
    var gameId = event.srcElement.id.split(':')[1];

    var gameStats = json[gameId];

    var predResult;

    if (gameStats['preds'] >= 0.05) {
        predResult = 'H'
    } else if (gameStats['preds'] <= -0.05){
        predResult = 'A'
    } else {
        predResult = 'D'
    };

    if (gameStats['FTR'] != 0) {

        if (predResult == gameStats['FTR']){
            var colorPred = '#42ffa7';
        } else {
            var colorPred = '#fd3772';
        }
    
    } else {
        var colorPred = '#eeff90';
    }

    $('#predictionTabPred').css('color',colorPred);

    var dateSplit = gameStats['Date'].split(' ')[0].split('-');
    var dateDisplay = parseInt(dateSplit[2]) + " " + monthsConvert[dateSplit[1]] + " " + dateSplit[0];

    var hTeam = gameStats['HomeTeam'];
    var aTeam = gameStats['AwayTeam'];
    
    if (hTeam in teamNameChange){
        hTeam = teamNameChange[hTeam]
    };
    if (aTeam in teamNameChange){
        aTeam = teamNameChange[aTeam]
    };

    var teamNames = hTeam + ' - ' + aTeam + '<br>' + dateDisplay;

    $('#predictionTabTeamNames').html(
        teamNames
    );

    var restulText;

    if (gameStats['FTR'] == 0){
        restulText = 'Result: TBD'
    } else {
        restulText = 'Result: ' + gameStats['GoalsFor_H']*10 + ' - ' + gameStats['GoalsFor_A']*10 + ' ' + gameStats['FTR']

    }

    $('#predictionTabRes').html(
        restulText
    );
    $('#predictionTabPred').html(
        'Predicted goal difference: ' + Math.round(gameStats['preds']*1000,2)/100 + ' ' + predResult
    );

    const oddsList = ['HomeOdds','DrawOdds','AwayOdds'];

    for (var i in oddsList){
        var odds = gameStats[oddsList[i]];

        $('#'+oddsList[i]).css('border','2px solid #36454f');

        $('#'+oddsList[i]).html(
            oddsList[i].charAt(0) + ': ' + Math.round(odds*20*100)/100
        );

        if (gameStats['FTR'] == oddsList[i].charAt(0)){
            $('#'+oddsList[i]).css('border','2px solid #888888');
        }

        if (predResult == oddsList[i].charAt(0)){
            $('#'+oddsList[i]).css('border','2px solid ' + colorPred);
        }

    }

    // DRAWING THE CHART

    var chartStats = {
        'HomeOdds': [],
        'DrawOdds': [],
        'AwayOdds': [],
        'T_GoalsFor_H': [],
        'T_GoalsAg_H': [],
        'T_GoalsFor_A': [],
        'T_GoalsAg_A': [],
        'T_Conversion_H': [],
        'T_Conversion_A': [],
        'T_Accuracy_H': [],
        'T_Accuracy_A': [],
        'T_Points_H': [],
        'T_Points_A': [],
        'L3M_Points_H': [],
        'L3M_Points_A': [],
        'T_TablePosition_H': [],
        'T_TablePosition_A': [],
        'T_Variance_H': [],
        'T_Variance_A': []
    }

    var chartXs = [gameStats['intercept']*10];

    for (var feature in chartStats){
        chartStats[feature].push(gameStats[feature]);
        chartStats[feature].push(gameStats['shap_'+feature]*10);

        chartXs.push(gameStats['shap_'+feature]*10);
    }

    var chartStatsConvert = {
        'HomeOdds': ['Home odds', 20],
        'DrawOdds': ['Draw odds', 20],
        'AwayOdds': ['Away odds', 20],
        'T_GoalsFor_H': ['Goals + (H)', 10],
        'T_GoalsAg_H': ['Goals - (H)', 10],
        'T_GoalsFor_A': ['Goals + (A)', 10],
        'T_GoalsAg_A': ['Goals - (A)', 10],
        'T_Conversion_H': ['Conversion (H)', 1],
        'T_Conversion_A': ['Conversion (A)', 1],
        'T_Accuracy_H': ['Accuracy (H)', 1],
        'T_Accuracy_A': ['Accuracy (A)', 1],
        'T_Points_H': ['Pts average (H)', 3],
        'T_Points_A': ['Pts average (A)', 3],
        'L3M_Points_H': ['Pts in last 3 (H)', 3],
        'L3M_Points_A': ['Pts in last 3 (A)', 3],
        'T_TablePosition_H': ['Table position (H)', 1],
        'T_TablePosition_A': ['Table position (A)', 1],
        'T_Variance_H': ['Variance (H)', 1],
        'T_Variance_A': ['Variance (A)', 1]
    }

    var chartYs = ['Intercept'];
    
    for (k in chartStatsConvert){
        chartYs.push(`${chartStatsConvert[k][0]}: ${Math.round(chartStats[k][0]*chartStatsConvert[k][1]*100)/100}`);
    };

    make1DPlot(chartXs, chartYs, 'chartCanvas');

};

// #######################    add listeners to 'how do I read this tab'    ##################################

document.getElementById('escButton').addEventListener('click', () => {
    $('#predictionTab').hide();
    $('#resultsMenu').show();    
});

// #######################    on page load: load games into left tab + add listeners to league buttons    ##################################

loadMatches(json, 'E0');

var leagueButtonsOnClick = function() {

    var leagueCode = this.id.split(':')[1];
    loadMatches(json, leagueCode);
    $('#predictionTab').hide();

};

var leagueButtons = document.getElementsByClassName("leagueButton");
Array.from(leagueButtons).forEach(function(element) {
    element.addEventListener('click', leagueButtonsOnClick);
});

// #######################    jquery button styling    ##################################

$(document).ready(function(){

    $('.topButton').hover(
        function () {							

            $(this).animate({
                backgroundColor: "#4f565a"
            }, 100 );

            $(this).css('cursor','pointer');

        },
        function () {

            $(this).animate({
                backgroundColor: "#36454f"
            }, 100 );

        }
    );

    $('.leagueButton').hover(
        function () {							

            $(this).animate({
                backgroundColor: "#4f565a"
            }, 100 );

            $(this).css('cursor','pointer');

        },
        function () {

            $(this).animate({
                backgroundColor: "#36454f"
            }, 100 );

        }
    );

});

// #######################    plots    ##################################

const plotMargin = 30;
const plotMarginLeft = 150;

const plotColor = '#2f363b';

function make1DPlot(xArray, yArray, targetDiv){

    var trace1 = {
        x: xArray,
        y: yArray,
        type: "waterfall",
        orientation: 'h',
        decreasing: { marker: { color: "#ff8181"} },
        increasing: { marker: { color: "#51ff94"} },
        connector: {
            mode: "between",
            line: {
                width: 0,
                color: "rgb(0, 0, 0)",
                dash: 0
            }
        }
    };
    
    var plotData = [trace1];

    var layout = {
        margin: {
            l: plotMarginLeft,
            r: plotMargin,
            b: plotMargin,
            t: plotMargin
        },
        title: {
            text:'SHAP local explanation',
            font: {
                family: 'Ubuntu',
                color: '#ffffff'
            }
        },
        xaxis:{
            title: {
                text: 'Predicted goal difference',
                font: {
                    color: '#ffffff',
                    size: 12
                }
            },
            tickfont: {
                family: 'Ubuntu',
                color: '#ffffff'
            },
            fixedrange: true,
        },
        yaxis:{
            autorange:'reversed',
            automargin: true,            
            tickfont: {
                family: 'Ubuntu',
                size: 14,
                color: '#ffffff',
                weight: 1000,
            },
            fixedrange: true,
        },
        plot_bgcolor: plotColor,
        paper_bgcolor: plotColor,
        height: 500
    };

    Plotly.newPlot(targetDiv, plotData, layout, {displayModeBar: false});

};

// #######################    last step, display content    ##################################

$('#mainContentDiv').show();    
