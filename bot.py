
from botcity.web import WebBot, Browser, By
from botcity.maestro import *
from botcity.web.util import element_as_select
from botcity.web.parsers import table_to_dict
from botcity.plugins.excel import BotExcelPlugin

BotMaestroSDK.RAISE_NOT_CONNECTED = False

excel = BotExcelPlugin()
excel.add_row(["CEP", "CIDADE", "POPULACAO"])

def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    # login com o BotCity para logs 
    #maestro.login(server="https://developers.botcity.dev", login="seulogin", key="suakey")

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Chrome
    bot.browser = Browser.CHROME

    #diretório do seu webdriver
    bot.driver_path = r"C:\chromedriver-win64\chromedriver.exe"

    # Opens the BotCity website.
    bot.browse("https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php")

    drop_uf = element_as_select(bot.find_element("//select[@id='uf']", By.XPATH))
    drop_uf.select_by_value("MG")
    bot.wait(15000)

    btn_pesquisar = bot.find_element("//button[@id='btn_pesquisar']", By.XPATH)
    btn_pesquisar.click()
    
    bot.wait(3000)

    table_dados = bot.find_element("//table[@id='resultado-DNEC']", By.XPATH)
    table_dados = table_to_dict(table=table_dados)
    
#    print(table_dados[0].keys())
        

    bot.navigate_to("https://cidades.ibge.gov.br/brasil/mg/panorama")

    int_Contador = 1
    str_CidadeAnterior = ""
    for cidade in table_dados:

        str_cidade = cidade["localidade"]
        str_cep = cidade["faixa_de_cep"]

        if str_CidadeAnterior == str_cidade:
            continue

        if int_Contador <= 5:
            campo_pesquisa = bot.find_element("//input[@placeholder='O que você procura?']", By.XPATH)
            campo_pesquisa.send_keys(str_cidade)

            opcao_cidade = bot.find_element(f"//a[span[contains(text(), '{str_cidade}')] and span[contains(text(), 'MG')]]", By.XPATH)
        
            bot.wait(1000)
            opcao_cidade.click()

            bot.wait(2000)

            populacao = bot.find_element("//div[@class='indicador__valor']", By.XPATH)
            str_populacao = populacao.text

            print(str_cep, str_cidade, str_populacao)
            excel.add_row([str_cep, str_cidade, str_populacao])
            # maestro.new_log_entry(activity_label="CIDADES", values={"CEP": f"{str_cep}", 
            #                     "CIDADE": f"{str_cidade}", "POPULACAO": f"{str_populacao}"})

            int_Contador += 1
            str_CidadeAnterior = str_cidade

        else:
            print("Numero de cidades já alcançada")
            break

    #seu diretório para salvar o arquivo excel
    excel.write(r"C:\Users\lucas\Documents\ProjetosBotCity\CidadesMG.xlsx")

    ...

    # Wait 3 seconds before closing
    bot.wait(5000)

    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    # maestro.finish_task(
    #     task_id=execution.task_id,
    #     status=AutomationTaskFinishStatus.SUCCESS,
    #     message="Task Finished OK."
    # )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
