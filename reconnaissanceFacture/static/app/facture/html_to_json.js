function tableToJson(table)
{
    var data = []

    var headers = []
    for (var i=0; i<table.rows[0].cells.length; i++)
    {
        headers[i] = table.rows[0].cells[i].innerHTML.toLowerCase().replace(/ /gi,'')
    }
    for (var i=1; i<table.rows.length; i++)
    {
        var tableRow = table.rows[i]
        var rowData = {} 
        for (var j=0; j<tableRow.cells.length; j++)
        {
            // console.log(tableRow.cells[j].lastElementChild.value)
            rowData[ headers[j] ] = tableRow.cells[j].lastElementChild.value
        }
        // console.log(rowData)
        data.push(rowData)
    }
    return data
}

function sendJson(foo,bar)
{
    var myjson = tableToJson(document.getElementById("prod_tab"))
    console.log('data',myjson)
    document.getElementById("jsonTable").value = JSON.stringify(myjson)
}
