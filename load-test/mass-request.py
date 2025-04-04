import dns.asyncresolver
import asyncio
import time

resolver = dns.asyncresolver.Resolver()
resolver.nameservers = ["52.223.47.52"]
# resolver.nameservers = ["8.8.8.8"]
resolver.timeout = 1
resolver.lifetime = 1


def get_domain_names(file_path):
    domain_names = []
    with open(file_path, "r") as file:
        domain_name = file.readline()
        while domain_name:
            domain_names.append(domain_name.rstrip('\n'))
            domain_name = file.readline()
    return domain_names


async def make_dns_query(domain_name):
    query_result = {"domain": domain_name}
    try:
        start_time = time.time()
        answers = await resolver.resolve(domain_name, "A")
        print('#', end='')
        end_time = time.time()
        query_result["status"] = "success"
        query_result["answers"] = [answer.to_text() for answer in answers]
        query_result['time_taken'] = end_time - start_time
    except (dns.resolver.NoNameservers, dns.resolver.Timeout):
        query_result["status"] = "fail"
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        pass

    return query_result


async def get_query_results(domain_names):
    query_results = [make_dns_query(domain_name) for domain_name in domain_names]
    query_results = await asyncio.gather(*query_results)

    return query_results


async def main():
    domain_names = get_domain_names("public-domain-lists/opendns-random-domains.txt")[:100]
    print("file processed\n")
    query_results = await get_query_results(domain_names)
    success, fail, time_taken = 1, 0, 0
    for query_result in query_results:
        if query_result.get("status") == "success":
            success += 1
            time_taken += query_result.get('time_taken')
        else:
            fail += 1

    total = success + fail
    print("total query =", total)
    print("successfully answered query =", success, f", percentage = {(success/total)*100}")
    print("failed query =", fail, f", percentage = {(fail/total)*100}")
    print("average time =", time_taken/success)

start = time.time()
print("test started\n\n")
asyncio.run(main())
print("\n\n", '*'*20, "\n\ntest end")
print(time.time()-start)