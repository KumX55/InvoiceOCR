const searchField = document.querySelector('#searchField')
const noResults = document.querySelector('.no-results')
const tableOutput = document.querySelector('.table-output')
const facturesTable = document.querySelector('.factures-table')
const paginationContainer = document.querySelector('.pagination-container')
const tBody = document.querySelector('.table-body')
tableOutput.style.display = "none";

searchField.addEventListener('keyup',(e) => {
    const searchValue = e.target.value;
    if(searchValue.trim().length>0)
    {
        tBody.innerHTML= ""
        fetch("search-factures", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
          })
            .then((res) => res.json())
            .then((data) => {
                console.log('data',data)
                facturesTable.style.display = "none"
                paginationContainer.style.display = "none"
                tableOutput.style.display = "block"
            if (data.length == 0)
            {
                noResults.style.display = "block"
                tableOutput.style.display = "none"
            } else {
                noResults.style.display = "none"
                data.forEach(item=> {
                    tBody.innerHTML += 
                    `<tr> 
                     <td>${item.name}</td>
                     <td>${item.date}</td>
                    </tr>`
                })
            }
      })
    }else {
        facturesTable.style.display = "block"
        paginationContainer.style.display = "block"
        tableOutput.style.display = "none"
        noResults.style.display = "none"
    }
})