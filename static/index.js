
// main script

$('#predictionTab').hide();

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

// console.log(json);

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

var canvas = document.getElementById("chartCanvas").getContext('2d');

const teamNameChange = {
    'Fortuna Dusseldorf':'Fortuna',
    'Union Berlin':'Union B.',
    'Bayern Munich':'Bayern',
    'Werder Bremen':'Werder',
    'Ein Frankfurt': 'Eintracht',
    'Leverkusen': 'Bayer 04',
    'Crystal Palace':'C Palace',
    'Sheffield United':'Sheffield',
    'Bournemouth':"B'mouth",
    'Southampton':"Soton",
    'Tottenham': 'Spurs',
    'Man United': 'Man Utd'
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
        var dateDisplay = dateSplit[2] + " " + monthsConvert[dateSplit[1]] + " " + dateSplit[0];

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


    var HDA = ['H', 'D', 'A'];

    for (var i in HDA){

        $('#valGames'+HDA[i]).html(
            countGames[HDA[i]]
        );

        $('#valAcc'+HDA[i]).html(
            Math.round(countWins[HDA[i]]*100/countGames[HDA[i]])+'%'
        );

        var returns = Math.round(sumReturn[HDA[i]]*100/countGames[HDA[i]]);

        if (returns>=0){
            var colorRet = '#42ffa7';
            var signRet = '+';
        } else {
            var colorRet = '#fd3772';
            var signRet = '-';
        }

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
    var dateDisplay = dateSplit[2] + " " + monthsConvert[dateSplit[1]] + " " + dateSplit[0];

    var hTeam = gameStats['HomeTeam'];
    var aTeam = gameStats['AwayTeam'];
    
    if (hTeam in teamNameChange){
        hTeam = teamNameChange[hTeam]
    };
    if (aTeam in teamNameChange){
        aTeam = teamNameChange[aTeam]
    };

    var teamNames = hTeam + ' - ' + aTeam + ', ' + dateDisplay;

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

    // DRAWING OF THE CHART

    const chartWidth = 200;
    const chartHeight = 500;

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

    // var chartYs = [];
    var chartXs = [gameStats['intercept']*10];

    for (var feature in chartStats){
        chartStats[feature].push(gameStats[feature]);
        chartStats[feature].push(gameStats['shap_'+feature]*10);

        chartXs.push(gameStats['shap_'+feature]*10);
    }

    for (var i = 1; i < chartXs.length; i++){
        chartXs[i] = chartXs[i] + chartXs[i-1]
    };

    var minXs = Math.min(...chartXs);
    var maxXs = Math.max(...chartXs);

    canvas.fillStyle = '#2f363b';
    canvas.clearRect(0, 0, chartWidth+1000, chartHeight);

    for (var i = 0; i < chartXs.length; i++){
        chartXs[i] = (chartXs[i] - minXs) / (maxXs - minXs)

        // draw on canvas

        var y = i*25;

        var changeX = chartXs[i]*chartWidth - chartXs[i-1]*chartWidth;

        if (changeX >= 0){
            canvas.fillStyle = '#74bbfb';
        } else {
            canvas.fillStyle = '#fd3772';
        };

        canvas.fillRect(250+50+chartXs[i-1]*chartWidth,y,changeX,10);

        // if ( i > 1 ){
        //     canvas.fillStyle = '#000000';
        //     canvas.fillRect(chartXs[i-1]*chartWidth,y-25+10,1,25-10);
        // }

    };

    canvas.fillStyle = '#000000';

    canvas.fillRect(250+50+chartXs[0]*chartWidth,20,1,chartHeight)

    canvas.beginPath();
    canvas.setLineDash([5, 15]);
    canvas.moveTo(250+50+chartXs[chartXs.length-1]*chartWidth,20);
    canvas.lineTo(250+50+chartXs[chartXs.length-1]*chartWidth+1,20+chartHeight);
    canvas.stroke();

    canvas.fillStyle = '#000000';
    canvas.font = "20px sans-serif";

    canvas.textAlign = 'end';
    canvas.fillText('Intercept: '+Math.round(gameStats['intercept']*1000)/100,250+chartXs[0]*chartWidth+20,y+10+30);
    canvas.fillText('Prediction: '+Math.round(gameStats['preds']*1000)/100,250+chartXs[chartXs.length-1]*chartWidth+20,y+10+30*2);

    var i = 1;

    var chartStatsConvert = {
        'HomeOdds': ['Home odds', 20],
        'DrawOdds': ['Draw odds', 20],
        'AwayOdds': ['Away odds', 20],
        'T_GoalsFor_H': ['H team, av goals scored', 10],
        'T_GoalsAg_H': ['H team, av goals conceded', 10],
        'T_GoalsFor_A': ['A team, av goals scored', 10],
        'T_GoalsAg_A': ['A team, av goals conceded', 10],
        'T_Points_H': ['H team, av points per game', 3],
        'T_Points_A': ['A team, av points per game', 3],
        'L3M_Points_H': ['H team, av points last 3 games', 3],
        'L3M_Points_A': ['A team, av points last 3 games', 3],
        'T_TablePosition_H': ['H team, Table position', 1],
        'T_TablePosition_A': ['A team, Table position', 1]
    }


    for (var feature in chartStats){

        var y = i*25;
        
        // canvas.fillStyle = '#000000';
        canvas.fillStyle = '#ffffff';
        canvas.font = "15px sans-serif";

        var textToFill = chartStatsConvert[feature][0] + ': ';
        var valToFill = Math.round(chartStats[feature][0]*chartStatsConvert[feature][1]*100)/100;

        canvas.textAlign = "end";
        canvas.fillText(textToFill,225,y+11);
        canvas.textAlign = "start";
        canvas.fillText(valToFill,230,y+11);

        i++;
    };

};

document.getElementById('escButton').addEventListener('click', () => {
    $('#predictionTab').hide();
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

