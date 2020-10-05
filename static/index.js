
// main script

$('#predictionTab').hide();
$('#backButtonUnderPredictionsTab').hide();
$('#howDoIReadThisButton').hide();

var league = 'E0';
// E0
// D1
// SP1
// I1
// F1

const fname = 'static/predicted.txt';

var json = (function () {
    var json = null;
    $.ajax({
        'type': 'GET',
        'async': false,
        'global': false,
        'url': fname,
        'dataType': "text",
        'success': function (data) {
            json = data;
        }
    });
    return json;
})(); 

json = JSON.parse(json);

function isMobileDevice() {
    return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
};

var mobileFlag = isMobileDevice();

// if iPad, change mobileFlag = false;
if (window.navigator.userAgent.search('iPad') != -1){
    mobileFlag = false;
};

function onlyUnique(value, index, self) { 
    return self.indexOf(value) === index;
}

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
    'Fortuna Dusseldorf':'Fortuna',
    'Union Berlin':'Union B.',
    'Bayern Munich':'Bayern',
    'Werder Bremen':'Werder',
    'Ein Frankfurt': 'Eintracht',
    'Leverkusen': 'Bayer 04',
    'Crystal Palace':'C. Palace',
    'Sheffield United':'Sheffield',
    'Bournemouth':"B'mouth",
    'Southampton':"So'ton",
    'Tottenham': 'Spurs',
    'Man United': 'Man Utd',
    'Sheffield Weds': 'Sheff. Weds',
    'Huddersfield': "Hud'field",
    'Middlesbrough': "M'brough",
    'PSV Eindhoven': 'PSV',
    'Sparta Rotterdam': 'Sparta R',
    'Pacos Ferreira': 'Pacos F',
    'Santa Clara': 'Santa C'
};

var loadMatches = function (json, league) {

    var jsonFilteredGames = {};

    for (var i in json){

        if (json[i]['Div'] == league){
            jsonFilteredGames[i] = json[i]
        };
    };

    var matchDates = [];

    for (var i in jsonFilteredGames){
        matchDates.push(jsonFilteredGames[i]['Date'].split(' ')[0]);
    };

    matchDates = matchDates.filter(onlyUnique).reverse();

    document.getElementById("resultsMenuGames").innerHTML = '';

    var countGamesDate = {};
    var sumReturnDate = {};

    for (var i = 0; i < matchDates.length; i++){

        var node = document.createElement("div");

        countGamesDate[matchDates[i]] = 0;
        sumReturnDate[matchDates[i]] = 0;

        var dateSplit = matchDates[i].split('-');
        var dateDisplay = parseInt(dateSplit[2]) + " " + monthsConvert[dateSplit[1]] + " " + dateSplit[0];

        var textnode = document.createElement('span');
        textnode.innerHTML = dateDisplay;

        var nodeDiv = document.createElement("div");
        nodeDiv.appendChild(textnode);

        var spanROI = document.createElement("span");
        spanROI.innerHTML = '+100% ROI';
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

        node.classList.add('button');
        node.innerHTML = hTeam + ' - ' + aTeam;
        node.id = 'game:' + i.toString();

        node.addEventListener('click', matchButtonsOnClick);

        var nodeDiv = document.createElement("div");

        var resultColorSpan = document.createElement("span");
        resultColorSpan.classList.add('resultColorSpan');
        resultColorSpan.style.backgroundColor = '#eeff90';
        resultColorSpan.style.color = '#eeff90';
        resultColorSpan.id = 'game:' + i.toString();

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

            resultColorSpan.style.backgroundColor = '#fd3772';
            resultColorSpan.style.color = '#fd3772';   

            if (jsonFilteredGames[i]['FTR'] == predResult){
                
                countWins[predResult]++;

                sumReturn[predResult] = sumReturn[predResult] + jsonFilteredGames[i][lookupOdds[predResult]]*20;
                sumReturnDate[matchDate] = sumReturnDate[matchDate] + jsonFilteredGames[i][lookupOdds[predResult]]*20;

                resultColorSpan.style.backgroundColor = '#42ffa7';
                resultColorSpan.style.color = '#42ffa7';        

            }
                
            sumReturn[predResult]--;
            sumReturnDate[matchDate]--;

        }

        resultColorSpan.innerHTML = '.';
        // resultColorSpan.innerHTML = predResult;

        node.appendChild(resultColorSpan);

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

            if (returnDate>=0){
                var colorRet = '#42ffa7';
                var signRetDate = '+';
            } else {
                var colorRet = '#fd3772';
                var signRetDate = '-';    
            }

            dateROItext = signRetDate + Math.abs(returnDate) + '% ROI';
        }

        document.getElementById('date:'+i+':ROI').innerHTML = dateROItext;
        document.getElementById('date:'+i+':ROI').style.color = colorRet;

    }


    $('.button').hover(
        function () {							

            $(this).animate({
                backgroundColor: "#777777"
            }, 100 );

            $(this).css('cursor','pointer');

        },
        function () {

            $(this).animate({
                backgroundColor: "#36454f"
            }, 100 );

        }
    );

}

const matchButtonsOnClick = function(event) {

    $('#predictionTab').show();

    if (mobileFlag==true){
        $('#backButtonUnderPredictionsTab').show();
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
        'T_Points_H': [],
        'T_Points_A': [],
        'L3M_Points_H': [],
        'L3M_Points_A': [],
        'T_TablePosition_H': [],
        'T_TablePosition_A': []
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
        'T_Points_H': ['Pts average (H)', 3],
        'T_Points_A': ['Pts average (A)', 3],
        'L3M_Points_H': ['Pts in last 3 (H)', 3],
        'L3M_Points_A': ['Pts in last 3 (A)', 3],
        'T_TablePosition_H': ['Table position (H)', 1],
        'T_TablePosition_A': ['Table position (A)', 1]
    }

    var chartYs = ['Intercept'];
    
    for (k in chartStatsConvert){
        chartYs.push(`${chartStatsConvert[k][0]}: ${Math.round(chartStats[k][0]*chartStatsConvert[k][1]*100)/100}`);
    };

    make1DPlot(chartXs, chartYs, 'chartCanvas');

};

document.getElementById('escButton').addEventListener('click', () => {
    $('#predictionTab').hide();
    $('#backButtonUnderPredictionsTab').hide();
    $('#resultsMenu').show();    
});

document.getElementById('backButtonUnderPredictionsTab').addEventListener('click', () => {
    $('#predictionTab').hide();
    $('#backButtonUnderPredictionsTab').hide();
    $('#resultsMenu').show();    
});

document.getElementById('howDoIReadThisButton').addEventListener('click', () => {
    $('#darkBackground').css('display','block');
    $('#howDoIReadThisTab').css('display','block');
});

document.getElementById('darkBackground').addEventListener('click', () => {
    $('#darkBackground').css('display','none');
    $('#howDoIReadThisTab').css('display','none');
});

loadMatches(json, 'E0');

var leagueButtons = document.getElementsByClassName("leagueButton");

var leagueButtonsOnClick = function() {

    var leagueCode = this.id.split(':')[1];
    loadMatches(json, leagueCode);
    $('#predictionTab').hide();

};

Array.from(leagueButtons).forEach(function(element) {
    element.addEventListener('click', leagueButtonsOnClick);
});

$(document).ready(function(){

    $('.topButton').hover(
        function () {							

            $(this).animate({
                backgroundColor: "#777777"
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
                backgroundColor: "#777777"
            }, 100 );

            $(this).css('cursor','pointer');

        },
        function () {

            $(this).animate({
                backgroundColor: "#36454f"
            }, 100 );

        }
    );

    $('#darkBackground').hover(
        function () {							
            $(this).css('cursor','pointer');
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
            text:'XGBoost model, SHAP local explanation',
            font: {
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
                family: 'sans-serif',
                color: '#ffffff'
            }
        },
        yaxis:{
            autorange:'reversed',
            automargin: true,            
            tickfont: {
                family: 'sans-serif',
                size: 14,
                color: '#ffffff'
            }
        },
        plot_bgcolor: plotColor,
        paper_bgcolor: plotColor
    };

    Plotly.newPlot(targetDiv, plotData, layout);

};

